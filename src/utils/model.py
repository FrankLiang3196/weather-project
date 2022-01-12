# encdoing: utf-8
"""
@Project: aqi_qixiangju
@File:    model
@Author:  Jiachen Zhao
@Time:    2021/11/11 18:28
@Description: 
"""

import abc
import numpy as np
import torch
import torch.nn as nn
from torch.autograd import Variable


from src.utils.develop_utils import load_parameter
from src.utils.utils import *

# MODEL_DIR = "./model_files"

class PyTorchUtils(metaclass=abc.ABCMeta):
    def __init__(self, seed, gpu):
        self.gpu = gpu
        self.seed = seed
        if self.seed is not None:
            torch.manual_seed(self.seed)
            torch.cuda.manual_seed(self.seed)
        self.framework = 0

    @property
    def device(self):
        return torch.device(f'cuda:{self.gpu}' if torch.cuda.is_available() and self.gpu is not None else 'cpu')

    def to_var(self, t, **kwargs):
        # ToDo: check whether cuda Variable.
        t = t.to(self.device)
        return Variable(t, **kwargs)

    def to_device(self, model):
        model.to(self.device)

    def get_parameter_number(self):
        total_num = sum(p.numel() for p in self.parameters())
        trainable_num = sum(p.numel() for p in self.parameters() if p.requires_grad)
        return {'Total': total_num, 'Trainable': trainable_num}


class NaiveTorchForecaster(PyTorchUtils, nn.Module):
    def __init__(self, args):
        nn.Module.__init__(self)
        PyTorchUtils.__init__(self, seed=1, gpu=None)
        self.net = nn.Linear(args.input_window_width, 1)
        self.net.weight = torch.nn.Parameter(torch.Tensor(np.ones([1, args.input_window_width])
                                                          / args.input_window_width))  # 取平均，权值为 1/args.input_window_width
        self.net.bias = torch.nn.Parameter(torch.Tensor([0]))
        self.net = nn.Sequential(self.net)
        self.args = args

    def to_tensor(self, X=None, y=None):  # X转为浮点类，Y转为整数类
        if X is not None:
            if type(X) is np.ndarray:
                X = self.to_var(torch.from_numpy(X).float())
            elif torch.is_tensor(X):
                X = self.to_var(X.float())
        if y is not None:
            if type(y) is np.ndarray:
                y = self.to_var(torch.from_numpy(y).int())
            elif torch.is_tensor(y):
                y = self.to_var(y.int())
        return X, y

    def fit(self, X=None, y=None):

        save_obj(self, name='naive_torch_forecaster', path=self.args.model_dir)
        pass

    def load_model(self):
         return load_obj('naive_torch_forecaster', path=self.args.model_dir)

    def predict(self, X):  # 单步预测

        # X shape: [num of stations, past time length, num of features] with time order t-5, t-4, ..., t-1, t
        self.net.eval()
        X, _ = self.to_tensor(X)
        Y_hat = [self.net.forward(X[:, :, i]).cpu().detach().numpy() for i in range(X.shape[-1])]  # 对选定特征进行预测，并转换为数组类型 array
        Y_hat = np.concatenate(Y_hat, axis=1) # [num of stations, num of features] 拼接

        return Y_hat


if __name__ == "__main__":
    print('-----')
    args = load_parameter('config')
    input = np.array([[[1,2], [2,3], [3,5], [4,5], [5,7], [6,8]], [[3,2], [4,3], [6,5], [5,5], [7,7], [7,8]]])
    forecaster = NaiveTorchForecaster(args)
    forecaster.fit()
    # forecaster = load_obj('naive_torch_forecaster', path=MODEL_DIR)
    y_hat = forecaster.predict(input)
    print(y_hat.round(2))