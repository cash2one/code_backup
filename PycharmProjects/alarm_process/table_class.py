from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, BigInteger, Float, create_engine,DateTime
from datetime import datetime
Base = declarative_base()


class ModuleAlarm(Base):
    __tablename__ = 'module_alarm'

    module_id = Column('module_id', BigInteger, autoincrement=True, primary_key=True)
    sms_id = Column('sms_id', BigInteger, nullable=False)
    module = Column('module', String(64))
    uri = Column('uri', String(255))
    latency = Column('latency', Integer, default=0, nullable=False)
    err_ratio = Column('err_ratio', Float, default=0.0, nullable=False)
    level = Column('level', Integer, default=0, nullable=False)
    state = Column('state', Integer, default=0, nullable=False)
    send_time = Column('send_time', DateTime)

    def __init__(self, sms_id, module, uri, latency, err_ratio, level=0, state=0,
                 send_time=datetime.now()):
        self.sms_id = sms_id
        self.module = module
        self.uri = uri
        self.latency = latency
        self.err_ratio = err_ratio
        self.level = level
        self.state = state
        self.send_time = send_time


def create_table():
    engine = create_engine('mysql://oc:oc@10.101.1.141:3306/oc', echo=False)
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    create_table()
    pass
