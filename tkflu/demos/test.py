import numpy as np

float1 = 1.0
float2 = 5.0
steps = 10  # 生成 10 个点

floats = np.linspace(float1, float2, steps).tolist()
print(floats)
