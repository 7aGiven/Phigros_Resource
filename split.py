import os
import subprocess
import math
from multiprocessing import Pool

def process_file(input):
    segment = 5  # 每段音频的长度，单位为秒
    start_offset = 20  # 开头不需要的部分，单位为秒
    end_offset = 20  # 结尾不需要的部分，单位为秒

    if input.endswith('.wav'):
        input_path = os.path.join('music', input)
        duration = subprocess.check_output(f'ffmpeg -i {input_path} 2>&1 | grep Duration | cut -d " " -f 4 | sed s/,//', shell=True).decode().strip()
        h, m, s = map(float, duration.split(':'))
        length = math.floor(h * 3600 + m * 60 + s)
        output_dir = f'splited_music/{os.path.splitext(input)[0]}'
        os.makedirs(output_dir, exist_ok=True)
        counter = 1
        for start in range(start_offset, length - end_offset, segment):
            output_path = os.path.join(output_dir, f'{counter}.wav')
            subprocess.call(f'ffmpeg -i {input_path} -ss {start} -t {segment} -acodec copy {output_path}', shell=True)
            print(f'裁剪音频：{output_path}')
            counter += 1
        new_output_dir = os.path.join(os.path.dirname(output_dir), os.path.basename(input_path))
        os.rename(output_dir, new_output_dir)
        print(f'移动文件夹：{output_dir} -> {new_output_dir}')

if __name__ == '__main__':
    with Pool() as p:
        p.map(process_file, os.listdir('music'))
