"""Seekable, verified HTTPS Range reader for Rasterio's Python VSI opener.

This avoids Windows Schannel credential acquisition. TLS certificates remain
verified by requests. Only 206 responses with matching Content-Range are used.
"""
import io,re,shutil
from pathlib import Path
import requests
def check_download_space():
    """Check the source workspace drive before each imagery range transfer."""
    if shutil.disk_usage(Path(__file__).anchor).free<1_200_000_000:
        raise OSError('Imagery transfer stopped below 1.2 GB free')
class RangeReader(io.RawIOBase):
    def __init__(self,url,mode='rb'):
        super().__init__()
        if not url.endswith('.tif'):raise FileNotFoundError(url)
        self.url=url;self.name=url;self.mode=mode;self.position=0;self.block=256*1024;self.cache={};self.session=requests.Session()
        self.session.headers['User-Agent']='IndusResearchInfrastructure/1.0'
        check_download_space()
        r=self.session.get(url,headers={'Range':'bytes=0-16383'},timeout=60);r.raise_for_status()
        if r.status_code!=206:raise ValueError('server did not honour HTTP range request')
        match=re.fullmatch(r'bytes 0-([0-9]+)/([0-9]+)',r.headers.get('Content-Range',''))
        if not match:raise ValueError('invalid Content-Range')
        self.length=int(match[2]);self.header=r.content;self.requests=1;self.transferred=len(r.content)
    def readable(self):return True
    def seekable(self):return True
    def writable(self):return False
    def tell(self):return self.position
    def seek(self,offset,whence=0):
        self.position=int(offset if whence==0 else self.position+offset if whence==1 else self.length+offset)
        if self.position<0:raise ValueError('negative seek')
        return self.position
    def read(self,size=-1):
        if size<0:size=self.length-self.position
        end=min(self.length,self.position+size)
        if self.position>=end:return b''
        if end<=len(self.header):
            out=self.header[self.position:end];self.position=end;return out
        parts=[]
        while self.position<end:
            block=self.position//self.block
            if block not in self.cache:
                start=block*self.block;stop=min(self.length-1,start+self.block-1)
                for attempt in range(3):
                    check_download_space()
                    r=self.session.get(self.url,headers={'Range':f'bytes={start}-{stop}'},timeout=60)
                    if r.status_code not in [429,500,502,503,504]:break
                    __import__('time').sleep(2**attempt)
                r.raise_for_status()
                if r.status_code!=206 or r.headers.get('Content-Range')!=f'bytes {start}-{stop}/{self.length}':raise ValueError('range reply mismatch')
                self.cache[block]=r.content;self.requests+=1;self.transferred+=len(r.content)
            offset=self.position-block*self.block;chunk=self.cache[block][offset:offset+end-self.position]
            if not chunk:raise IOError('empty range block')
            parts.append(chunk);self.position+=len(chunk)
        return b''.join(parts)
    def readinto(self,b):
        data=self.read(len(b));b[:len(data)]=data;return len(data)
    def close(self):
        if hasattr(self,'cache'):self.cache.clear()
        if hasattr(self,'session'):self.session.close()
        super().close()
