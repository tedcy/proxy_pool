import tracemalloc
import threading
import time
import gc
from handler.logHandler import LogHandler

class MemoryChecker:
    def __init__(self, top=10, traceback_limit=25, interval=60):
        """
        初始化内存统计类
        :param top: 输出内存占用最多的前top个位置
        :param traceback_limit: 调用栈记录深度
        :param interval: 自动dump内存统计的时间间隔（秒），默认5分钟
        """
        self.top = top
        self.traceback_limit = traceback_limit
        self.interval = interval
        self.log = LogHandler("memory")
        self.started = False
        self._thread = None
        self._gcThread = None
        self._stop_event = threading.Event()

    def start(self):
        """开始内存统计并启动自动dump线程"""
        if not self.started:
            tracemalloc.start(self.traceback_limit)
            self.started = True
            self.log.info("MemoryChecker started.")
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._periodic_dump, daemon=True)
            self._gcThread = threading.Thread(target=self._gc, daemon=True)
            self._thread.start()
            self._gcThread.start()

    def stop(self):
        """停止内存统计并停止自动dump线程"""
        if self.started:
            self._stop_event.set()
            if self._thread:
                self._thread.join()
            tracemalloc.stop()
            self.started = False
            self.log.info("MemoryChecker stopped.")

    def dump_top_stats(self):
        """输出当前内存占用最多的位置到日志"""
        if not self.started:
            self.log.warning("MemoryChecker not started yet.")
            return

        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('traceback')

        self.log.info("[内存占用最多的%d个调用栈]", self.top)
        for index, stat in enumerate(top_stats[:self.top], 1):
            self.log.info("#%d: 共分配了 %.1f KiB 内存，%d 个对象",
                          index, stat.size / 1024, stat.count)
            for line in stat.traceback.format():
                self.log.info("    %s", line)

    def _periodic_dump(self):
        """后台线程定时dump内存统计"""
        while not self._stop_event.wait(self.interval):
            self.log.info("自动定时dump内存统计开始")
            self.dump_top_stats()
            self.log.info("自动定时dump内存统计结束")
    
    def _gc(self):
        """后台线程定时执行垃圾回收"""
        while not self._stop_event.wait(1):
            self.log.info("自动执行垃圾回收开始")
            gc.collect()
            self.log.info("自动执行垃圾回收结束")