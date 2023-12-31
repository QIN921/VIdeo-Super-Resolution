import argparse
import glob
import os
import cv2
import mmcv
import numpy as np
import torch
from mmcv.runner import load_checkpoint
from mmedit.core import tensor2img
from tqdm import trange
from .models.builder import build_model


VIDEO_EXTENSIONS = ('.mp4', '.mov')
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:256"


def parse_args():
    parser = argparse.ArgumentParser(
        description='Inference script of RealBasicVSR')
    parser.add_argument('--config', default='./realbasicvsr/configs/realbasicvsr_x4.py', required=False, help='test config file path')
    parser.add_argument('--checkpoint', default='./realbasicvsr/checkpoints/RealBasicVSR_x4.pth', required=False, help='checkpoint file')
    parser.add_argument('--input_dir', default='./data/frame',required=False,  help='directory of the input video')
    parser.add_argument('--output_dir', default='./data/output',required=False,  help='directory of the output video')
    parser.add_argument(
        '--max_seq_len',
        type=int,
        default=8,required=False,
        help='maximum sequence length to be processed')
    parser.add_argument(
        '--is_save_as_png',
        type=bool,
        default=True,required=False,
        help='whether to save as png')
    parser.add_argument(
        '--fps', type=float, default=25,required=False,  help='FPS of the output video')
    args = parser.parse_args()

    return args


def init_model(config, checkpoint=None):
    """Initialize a model from config file.

    Args:
        config (str or :obj:`mmcv.Config`): Config file path or the config
            object.
        checkpoint (str, optional): Checkpoint path. If left as None, the model
            will not load any weights.
        device (str): Which device the model will deploy. Default: 'cuda:0'.

    Returns:
        nn.Module: The constructed model.
    """

    if isinstance(config, str):
        config = mmcv.Config.fromfile(config)
    elif not isinstance(config, mmcv.Config):
        raise TypeError('config must be a filename or Config object, '
                        f'but got {type(config)}')
    config.model.pretrained = None
    config.test_cfg.metrics = None
    model = build_model(config.model, test_cfg=config.test_cfg)
    if checkpoint is not None:
        checkpoint = load_checkpoint(model, checkpoint)

    model.cfg = config  # save the config in the model for convenience
    model.eval()

    return model


def realbasicvsr(socktio):
    # 输入输出只是文件夹
    args = parse_args()

    # initialize the model
    socktio.emit('server_response', {'data': "模型加载中，请稍候"})
    model = init_model(args.config, args.checkpoint)
    
    # read images
    file_extension = os.path.splitext(args.input_dir)[1]
    if file_extension == '':  # input is a directory
        inputs = []
        input_paths = sorted(glob.glob(f'{args.input_dir}/*'))
        for input_path in input_paths:
            img = mmcv.imread(input_path, channel_order='rgb')
            inputs.append(img)
    else:
        raise ValueError('"input_dir" can only be a directory.')

    for i, img in enumerate(inputs):
        img = torch.from_numpy(img / 255.).permute(2, 0, 1).float()
        inputs[i] = img.unsqueeze(0)
    inputs = torch.stack(inputs, dim=1)

    # map to cuda, if available
    cuda_flag = False
    if torch.cuda.is_available():
        model = model.cuda()
        cuda_flag = True
    socktio.emit('server_response', {'data': "模型加载完毕，开始处理"})
    mmcv.mkdir_or_exist(args.output_dir)
    with torch.no_grad():
        if isinstance(args.max_seq_len, int):
            outputs = []
            for i in trange(0, inputs.size(1), args.max_seq_len):
                imgs = inputs[:, i:i + args.max_seq_len, :, :, :]
                if cuda_flag:
                    imgs = imgs.cuda()
                outputs.append(model(imgs, test_mode=True)['output'].cpu())
                outputs = torch.cat(outputs, dim=1)
                for j in range(0, outputs.size(1)):
                    output = tensor2img(outputs[:, j, :, :, :])
                    filename = os.path.basename(input_paths[i+j])
                    if args.is_save_as_png:
                        file_extension = os.path.splitext(filename)[1]
                        filename = filename.replace(file_extension, '.png')
                    mmcv.imwrite(output, f'{args.output_dir}/{filename}')
                    socktio.emit('server_response_num', {'data': (i+j+1) / inputs.size(1)})
                outputs = []
        else:
            if cuda_flag:
                inputs = inputs.cuda()
            outputs = model(inputs, test_mode=True)['output'].cpu()
            for i in trange(0, outputs.size(1)):
                output = tensor2img(outputs[:, i, :, :, :])
                filename = os.path.basename(input_paths[i])
                if args.is_save_as_png:
                    file_extension = os.path.splitext(filename)[1]
                    filename = filename.replace(file_extension, '.png')
                mmcv.imwrite(output, f'{args.output_dir}/{filename}')

