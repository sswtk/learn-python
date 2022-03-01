"""
@Time    : 2022/3/1 9:37
@Author  : ssw
@File    : helper_sftp_uploaddown_file.py
@Desc    :在服务器中通过sftp上传下载文件
"""
import ftplib
import shutil
import os
import time
# import sftplib
# import socket

class MySftp:
    # socket.setdefaulttimeout(99999999)
    ftp = ftplib.FTP(timeout=9999999)
    bIsDir = False
    path = ""


    def __init__(self, host, port=21):
        self.host = host
        # self.ftp.set_debuglevel(2) #打开调试级别2，显示详细信息
        # self.ftp.set_pasv(0)      #0主动模式 1 #被动模式
        self.ftp.connect(host, port)


    def Login(self, user, passwd):
        # self.pool.submit(self.ftp.login,user, passwd)
        print(self.ftp.login(user, passwd))
        # self.ftp_host = self.pool.submit(ftputil.FTPHost,self.host, user, passwd).result()
        self.ftp_host = ftputil.FTPHost(self.host, user, passwd)

    def DownLoadFile(self, LocalFile, RemoteFile):
        file_handler = open(LocalFile, 'wb')
        self.ftp.retrbinary("RETR %s" % (RemoteFile), file_handler.write)
        file_handler.close()
        return True

    def UpLoadFile(self, LocalFile, RemoteFile):
        if os.path.isfile(LocalFile) == False:
            return False
        file_handler = open(LocalFile, "rb")
        self.ftp.storbinary('STOR %s' % RemoteFile, file_handler, 4096)
        file_handler.close()
        return True

    def UpLoadFileTree(self, LocalDir, RemoteDir):
        if os.path.isdir(LocalDir) == False:
            return False
        LocalNames = os.listdir(LocalDir)
        # 先在远端创建目录
        self.ftp.mkd(RemoteDir)
        self.ftp.cwd(RemoteDir)
        for Local in LocalNames:
            src = os.path.join(LocalDir, Local)
            if os.path.isdir(src):
                self.UpLoadFileTree(src, Local)
            else:
                self.UpLoadFile(src, Local)

        self.ftp.cwd("..")
        return

    def DownLoadFileTree(self, LocalDir, RemoteDir):
        if os.path.isdir(LocalDir) == False:
            os.makedirs(LocalDir)
        self.ftp.cwd(RemoteDir)
        RemoteNames = self.ftp.nlst()
        for file in RemoteNames:
            Local = os.path.join(LocalDir, file)
            print(self.isDir(file))
            if self.isDir(file):
                self.DownLoadFileTree(Local, file)
            else:
                self.DownLoadFile(Local, file)
        self.ftp.cwd("..")
        return

    def SynchroFileTree2Ftp(self, LocalDir, RemoteDir):
        if os.path.isdir(LocalDir) == False:
            return False
        LocalNames = os.listdir(LocalDir)
        try:
            self.ftp_host.rmtree(RemoteDir)
        except:
            print("删除失败")
        self.ftp.mkd(RemoteDir)
        self.ftp.cwd(RemoteDir)
        for Local in LocalNames:
            src = os.path.join(LocalDir, Local)
            if os.path.isdir(src):
                self.UpLoadFileTree(src, Local)
            else:
                self.UpLoadFile(src, Local)

        self.ftp.cwd("..")

        return

    def SynchroFileTree2Local(self, LocalDir, RemoteDir):
        if os.path.isdir(LocalDir) == False:
            os.makedirs(LocalDir)
        else:
            shutil.rmtree(LocalDir)
            os.makedirs(LocalDir)
        self.ftp.cwd(RemoteDir)
        RemoteNames = self.ftp.nlst()
        for file in RemoteNames:
            Local = os.path.join(LocalDir, file)
            if self.isDir(file):
                self.DownLoadFileTree(Local, file)
            else:
                self.DownLoadFile(Local, file)
        self.ftp.cwd("..")
        return

    def get_dic_size(self, path):
        size = 0
        for i in self.ftp_host.listdir(path):
            if self.isDir(path+'/'+i):
                size += self.get_dic_size(path+'/'+i)
            else:
                size += self.ftp_host.lstat(path+'/'+i).st_size
        return size

    def get_file_dic(self):
        ftp_file_dic = {}
        for f in self.ftp_host.listdir("."):
            if self.isDir(f):
                print(f)
                info = self.ftp_host.lstat(f)
                ftp_file_dic[f] = [info.st_mtime, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(info.st_mtime)), self.get_dic_size(f)]
            else:
                info = self.ftp_host.lstat(f)
                # print(self.ftp_host.lstat(f))
                ftp_file_dic[f] = [info.st_mtime, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(info.st_mtime)), info.st_size]
        return ftp_file_dic

    def isDir(self, path):
        if self.ftp_host.path.isdir(path):
            return True

    def close(self):
        self.ftp.quit()


if __name__ == "__main__":

    ftp = MySftp('192.168.10.130')
    ftp.Login('ft', 'password')
    print(ftp.get_dic_size('del'))
        # ftp.get_file_dic()
    # print(ftp.ftp_host.stat('dir4'))

    # 下载时候远端地址不需要/
    # ftp.DownLoadFileTree('file/del', 'del')  # ok
    # 上传时候远端地址要用绝对地址
    # ftp.UpLoadFileTree('file/dir1', "dir1")
    # print(ftp.isDir('del'))