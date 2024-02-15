import numpy as np
import torch
import sklearn

if __name__ == '__main__':
    print(f'numpy version : {np.__version__}')
    print(f'torch version : {torch.__version__}')
    print(f'sklearn version : {sklearn.__version__}')
    print(f'CUDA 프로그래밍 가능여부 :  {torch.cuda.is_available()}')
    print(f'CUDA 프로그래밍 가능여부 : {torch.cuda.get_device_name()}')
    print(f'사용 가능 GPU 갯수 :  {torch.cuda.device_count()}')

    C:\Users\cwh92\anaconda3
    C:\Users\cwh92\anaconda3\Scripts
    C:\Users\cwh92\anaconda3\Library\bin
    C:\Users\cwh92\anaconda3\Library