import os
import subprocess
os.system('chcp 65001')
os.system('./realcugan/realcugan-ncnn-vulkan.exe -i ./data/frame -s 2 -o ./data/output')

# 定义 .exe 文件路径
exe_path = './realcugan/realcugan-ncnn-vulkan.exe'

# 定义需要传递给 .exe 文件的参数列表
args = ['-i ./data/frame', '-s 2', '-o ./data/output']

# 调用 .exe 文件并传递参数
process = subprocess.run('./realcugan/realcugan-ncnn-vulkan.exe -i ./data/frame -s 2 -o ./data/output', capture_output=True, text=True)

# 输出命令的输出和错误信息
print(process.stdout)
print(process.stderr)
