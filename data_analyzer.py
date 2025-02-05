# --*-- coding:utf-8 --*--
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import configparser
import random
from datetime import datetime


def analyze_data(log_path):
    df = pd.read_csv(log_path)

    # 数据清洗：去除极端值
    df = df[(df['温度(℃)'] >= 0) & (df['温度(℃)'] <= 150)]
    df = df[(df['压力(kPa)'] >= 20) & (df['压力(kPa)'] <= 100)]

    # 标记异常数据
    df['温度异常'] = df['温度(℃)'] > 100
    df['压力异常'] = df['压力(kPa)'] < 50
    df['综合异常'] = df['温度异常'] | df['压力异常']

    # 设置主题风格
    sns.set(style="whitegrid")

    # 生成可视化报告
    plt.figure(figsize=(18, 10))  # 增大图像尺寸
    plt.plot(df['时间'], df['温度(℃)'], label='Temp(℃)', color='blue', linewidth=1.5)
    plt.plot(df['时间'], df['压力(kPa)'], label='Pressure(kPa)', color='green', linewidth=1.5)
    plt.axhline(y=100, color='red', linestyle='--', linewidth=1.2, label='Temperature alarm line')
    plt.axhline(y=50, color='orange', linestyle='--', linewidth=1.2, label='Pressure alarm line')

    # 添加标题和轴标签
    plt.title('analysis report', fontsize=20)
    # plt.xlabel('Time', fontsize=16)
    plt.ylabel('Temp / Pressure', fontsize=16)

    # 设置图例
    plt.legend(loc='upper right', fontsize=14)

    # 格式化 X 轴标签，减少标签数量
    plt.xticks(df['时间'][::60], rotation=45, ha='right', fontsize=12)  # 每隔60个点显示一个标签

    # 添加网格线
    plt.grid(True, linestyle='--', alpha=0.7)

    # 调整布局
    plt.tight_layout()

    # 保存图片
    report_path = f'report_{datetime.now().strftime("%Y%m%d")}.png'
    plt.savefig(report_path, dpi=300)
    plt.close()

    # 返回异常数据
    abnormal = df[df['综合异常']]
    return abnormal, report_path


# 发送邮件通知
def send_email(receiver, report_path, config):
    msg = MIMEMultipart()
    msg['Subject'] = '设备异常报告'
    msg['From'] = config['EMAIL']['sender']
    msg['To'] = receiver

    # 正文内容
    body = "发现设备异常数据，请查看附件报告。"
    msg.attach(MIMEText(body, 'plain'))

    # 添加报告附件
    with open(report_path, 'rb') as f:
        attach = MIMEApplication(f.read(), _subtype='png')
        attach.add_header('Content-Disposition', 'attachment', filename=report_path)
        msg.attach(attach)

    # 发送邮件
    with smtplib.SMTP(config['EMAIL']['smtp_server'], int(config['EMAIL']['smtp_port'])) as server:
        server.login(config['EMAIL']['sender'], config['EMAIL']['password'])
        server.send_message(msg)


if __name__ == "__main__":
    # 加载配置
    config = configparser.ConfigParser()
    config.read('src/config.ini')

    # 分析数据
    abnormal, report_path = analyze_data('equipment_log_sample.csv')

    # 发送邮件（需配置真实邮箱）
    if not abnormal.empty:
        send_email(config['EMAIL']['receiver'], report_path, config)
        print("发现异常并已发送报告！")
    else:
        print("设备运行正常。")