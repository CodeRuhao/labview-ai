# 介绍
本代码库主要展示多个AI相关（尤其是大语言模型）的Demo
- LabVIEW调用本地大模型
- LabVIEW搭建本地知识库

# 准备工作

## LabVIEW环境设置
- 安装LabVIEW 2023或以上版本
- 通过VI Package Manager(VIPM)安装JKI JSON工具包

## Python环境设置
- 安装Python 3.10
  https://www.python.org/downloads/release/python-31011/

- 设置Python虚拟环境（Windows）

    ```cmd
    mkdir c:\dev\
    cd c:\dev\
    python -m venv labview-ai
    .\labview-ai\Scripts\activate
    ```

- 安装需要的Python库

    ```cmd
    cd <本代码库所在文件夹>
    pip install -r requirements.txt
    ```

# Demo

## 下载开源大模型

- 下载并安装LM Studio
  https://lmstudio.ai/

  ![lmstudio](docs/.img/image.png)

- 在LM Studio中搜索并下载开源大模型

  ![lmstudio_gif](docs/.img/LM_Studio.gif)

- 打开如下设置来启用本地访问

  ![alt text](docs/.img/image-1.png)

## LabVIEW调用本地开源大模型

- 打开"src\LabVIEW with Local Model.lvproj"

  ![alt text](docs/.img/image-2.png)

- 打开"LabVIEW调用本地大模型.vi"

  ![alt text](docs/.img/image-3.png)

## LabVIEW搭建本地知识库

- 打开"src\LabVIEW RAG.lvproj"

  ![alt text](docs/.img/image-4.png)

- 打开"LabVIEW结合知识库调用本地大模型.vi"

  ![alt text](docs/.img/image-5.png)