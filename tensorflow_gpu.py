import tensorflow as tf

print(f'TensorFlow version: {tf.__version__}')
print(f'CUDA 사용 가능 여부: {tf.test.is_built_with_cuda()}')
print(f'GPU 사용 가능 여부: {tf.config.list_physical_devices("GPU")}')


# TensorFlow version: 2.12.0
# CUDA 사용 가능 여부: False
# GPU 사용 가능 여부: []    
# PS D:\LT4\LTLUX_23.11.15\WebPlatform
