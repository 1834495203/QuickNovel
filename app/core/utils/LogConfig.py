import logging

def init_log():
    logging.basicConfig(
        level=logging.DEBUG,  # 设置为 DEBUG 以捕获所有日志
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def get_logger(name: str):
    return logging.getLogger(name)
