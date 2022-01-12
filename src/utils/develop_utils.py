# encdoing: utf-8
"""
@Project: aqi_qixiangju
@File:    develop_utils
@Author:  Jiachen Zhao
@Time:    2021/11/14 14:57
@Description: 
"""

import yaml, os, argparse
# how to install yaml, pip3 install pyyaml

# print(__name__)
# print(__package__)

def init_parser():
    parser = argparse.ArgumentParser(description='AQI forecasting')

    # Setting
    # parser.add_argument('--config', '-c', type=str, default='', help='ID of the using config', required=False)
    parser.add_argument('--input_dir', type=str, default='', help="Dir of input files")
    parser.add_argument('--output_dir', type=str, default='', help="Dir of output files")
    parser.add_argument('--model_dir', type=str, default='', help="Dir of model files")

    # Forecasting
    parser.add_argument('--input_window_width', type=int, help="The past time length feed into the model")
    parser.add_argument('--output_window_width', type=int, help="The future time length that we need to forecast")
    parser.add_argument('--start_time', type=str, default='', help="simulation starting time")
    parser.add_argument('--input_features', type=list, help="Features used to forecast")

    # Model
    parser.add_argument('--model_type', '-mt', type=str, default='', help="the forecasting model name")
    parser.add_argument('--model_args', default=dict(), help="Args for creating the model")
    return parser


# def load_parameter(file='config'):
#     parser = init_parser()
#     if os.path.exists(f'{file}.yaml'):
#         with open(f'{file}.yaml', 'r') as f:
#             yaml_arg = yaml.load(f, Loader=yaml.FullLoader)
#             parser.set_defaults(**yaml_arg)
#     else:
#         raise ValueError(f'Do NOT exist this file in {file}.yaml!')
#     return parser.parse_args()

def load_parameter(file='config', main_load=False):
    parser = init_parser()  # 初始化特征的种类
    # print(os.path.dirname(os.path.abspath('.')))
    # print(os.path.dirname(os.path.dirname(os.path.abspath('.'))) + '/' + f'{file}.yaml')
    if main_load:
        if os.path.exists(os.path.abspath('.') + '/' + f'{file}.yaml'):   # 从与config.yaml在同一目录位置下运行的路径
            with open(os.path.abspath('.') + '/' + f'{file}.yaml', 'rb') as f:  # 从与config.yaml在同一目录位置下运行的路径
                yaml_arg = yaml.load(f, Loader=yaml.FullLoader)
                parser.set_defaults(**yaml_arg)
        else:
            raise ValueError(f'Do NOT exist this file in {file}.yaml!')

    else:
        if os.path.exists(os.path.dirname(os.path.dirname(os.path.abspath('.'))) + '/' + f'{file}.yaml'):   # 直接运行model.py时的路径
            with open(os.path.dirname(os.path.dirname(os.path.abspath('.'))) + '/' + f'{file}.yaml', 'rb') as f:  # 直接运行model.py时的路径
                yaml_arg = yaml.load(f, Loader=yaml.FullLoader)
                parser.set_defaults(**yaml_arg)
        else:
            raise ValueError(f'Do NOT exist this file in {file}.yaml!')
    return parser.parse_args()


def try_args(args):
    print(type(args.input_dir))
    print(type(args.input_features))
    print(args.model_args)
    print(type(args.start_time))

if __name__ == "__main__":
    print('-----')
    # args = load_parameter(file='config')
    args = load_parameter('config')
    print(type(args))
    try_args(args)






