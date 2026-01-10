"""
SSH客户端连接管理器
用于建立和管理与云服务器的SSH连接
"""

import logging
import socket
from typing import Dict, Optional

import paramiko

logger = logging.getLogger(__name__)


class SSHClientManager:
    """SSH客户端连接管理器"""

    def __init__(
        self,
        host: str,
        port: int = 22,
        username: str = "root",
        password: Optional[str] = None,
        key_path: Optional[str] = None,
        passphrase: Optional[str] = None,
        timeout: int = 10,
    ):
        """
        初始化SSH客户端管理器

        Args:
            host: 服务器地址
            port: SSH端口，默认22
            username: SSH用户名
            password: SSH密码（密码认证时使用）
            key_path: SSH私钥路径（密钥认证时使用）
            passphrase: 私钥密码（如果私钥有密码）
            timeout: 连接超时时间（秒）
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key_path = key_path
        self.passphrase = passphrase
        self.timeout = timeout
        self.client = None
        self.is_connected = False

    def connect(self) -> bool:
        """
        建立SSH连接

        Returns:
            bool: 连接成功返回True，失败返回False

        Raises:
            Exception: 连接失败时抛出异常
        """
        try:
            # 创建SSH客户端实例
            self.client = paramiko.SSHClient()

            # 自动添加主机密钥（生产环境建议改为手动验证）
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # 选择认证方式
            if self.key_path:
                # 密钥认证
                logger.info(f"使用SSH密钥认证连接: {self.host}:{self.port}")
                try:
                    # 尝试加载RSA密钥
                    private_key = paramiko.RSAKey.from_private_key_file(self.key_path, password=self.passphrase)
                except paramiko.ssh_exception.PasswordRequiredException:
                    logger.error(f"私钥需要密码: {self.key_path}")
                    raise
                except paramiko.ssh_exception.SSHException:
                    # 如果不是RSA密钥，尝试其他类型
                    try:
                        private_key = paramiko.Ed25519Key.from_private_key_file(self.key_path, password=self.passphrase)
                        # 如果不是Ed25519密钥，尝试其他类型
                    except paramiko.ssh_exception.SSHException:
                        private_key = paramiko.ECDSAKey.from_private_key_file(self.key_path, password=self.passphrase)

                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    pkey=private_key,
                    timeout=self.timeout,
                    allow_agent=False,
                    look_for_keys=False,
                )

            else:
                # 密码认证
                logger.info(f"使用密码认证连接: {self.host}:{self.port}")
                if not self.password:
                    raise ValueError("密码认证需要提供password参数")

                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    timeout=self.timeout,
                    allow_agent=False,
                    look_for_keys=False,
                )

            self.is_connected = True
            logger.info(f"SSH连接成功: {self.username}@{self.host}:{self.port}")
            return True

        except paramiko.AuthenticationException as e:
            logger.error(f"SSH认证失败 {self.host}:{self.port} - {e}")
            self.is_connected = False
            raise Exception(f"SSH认证失败: {e}")

        except socket.timeout as e:
            logger.error(f"SSH连接超时 {self.host}:{self.port} - {e}")
            self.is_connected = False
            raise Exception(f"SSH连接超时: {e}")

        except socket.error as e:
            logger.error(f"网络连接失败 {self.host}:{self.port} - {e}")
            self.is_connected = False
            raise Exception(f"网络连接失败: {e}")

        except Exception as e:
            logger.error(f"SSH连接失败 {self.host}:{self.port} - {e}")
            self.is_connected = False
            raise

    def execute_command(self, command: str, timeout: int = 30) -> Dict[str, str]:
        """
        执行远程命令

        Args:
            command: 要执行的命令
            timeout: 命令执行超时时间（秒）

        Returns:
            Dict: {
                'stdout': 标准输出,
                'stderr': 标准错误,
                'exit_code': 退出码
            }

        Raises:
            Exception: 如果SSH未连接或命令执行失败
        """
        if not self.client or not self.is_connected:
            raise Exception("SSH未连接，请先调用connect()")

        try:
            logger.debug(f"执行命令: {command}")

            # 执行命令
            stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)

            # 读取输出
            stdout_data = stdout.read().decode("utf-8", errors="ignore").strip()
            stderr_data = stderr.read().decode("utf-8", errors="ignore").strip()
            exit_code = stdout.channel.recv_exit_status()

            result = {
                "stdout": stdout_data,
                "stderr": stderr_data,
                "exit_code": exit_code,
            }

            if exit_code != 0:
                logger.warning(f"命令执行失败 (退出码: {exit_code}): {command}")
                logger.warning(f"错误输出: {stderr_data}")
            else:
                logger.debug(f"命令执行成功: {command}")

            return result

        except socket.timeout:
            logger.error(f"命令执行超时: {command}")
            raise Exception(f"命令执行超时（{timeout}秒）: {command}")

        except Exception as e:
            logger.error(f"执行命令失败: {command} - {e}")
            raise

    def close(self):
        """关闭SSH连接"""
        if self.client:
            try:
                self.client.close()
                self.is_connected = False
                logger.info(f"SSH连接已关闭: {self.host}:{self.port}")
            except Exception as e:
                logger.error(f"关闭SSH连接失败: {e}")

    def is_alive(self) -> bool:
        """
        检查SSH连接是否仍然存活

        Returns:
            bool: 连接存活返回True，否则返回False
        """
        if not self.client or not self.is_connected:
            return False

        try:
            # 发送一个简单的命令测试连接
            transport = self.client.get_transport()
            if transport and transport.is_active():
                return True
            else:
                self.is_connected = False
                return False
        except Exception:
            self.is_connected = False
            return False

    def reconnect(self) -> bool:
        """
        重新连接

        Returns:
            bool: 重连成功返回True，失败返回False
        """
        logger.info(f"尝试重新连接: {self.host}:{self.port}")
        self.close()
        try:
            return self.connect()
        except Exception as e:
            logger.error(f"重连失败: {e}")
            return False

    def __enter__(self):
        """支持with语句"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持with语句"""
        self.close()
        return False

    def __del__(self):
        """析构函数，确保连接被关闭"""
        self.close()

    def __repr__(self):
        """字符串表示"""
        status = "已连接" if self.is_connected else "未连接"
        return f"<SSHClientManager {self.username}@{self.host}:{self.port} [{status}]>"
