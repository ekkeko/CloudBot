from cloudbot import hook
from cloudbot.event import EventType
from cloudbot.util import database
import datetime
from sqlalchemy import Table, Column, String, DateTime, PrimaryKeyConstraint, select

table = Table(
    'clientversion',
    database.metadata,
    Column('timestamp', DateTime),
    Column('chan', String),
    Column('nick', String),
    Column('mask', String),
    Column('version', String),
    PrimaryKeyConstraint('timestamp','mask')
)

@hook.on_start
def init_cc():
    global version
    versionbytes = bytearray([1])
    versionbytes.extend('VERSION'.encode('ascii'))
    version = versionbytes.decode('ascii')

@hook.event(EventType.join, singlethread=True)
def cc_onjoin(db, nick, chan, conn, mask):
    if not conn.nick == nick:
        now = datetime.datetime.now()
        if not db.query(table).filter(table.c.timestamp == now).filter(table.c.mask == mask).count():
            db.execute(table.insert().values(timestamp=now, chan=chan, nick=nick, mask=mask))
            db.commit()
        conn.ctcp(nick, "VERSION", "")

@hook.event(EventType.notice,singlethread=True)
def cc_version(db, nick, conn, content, mask):
    if content.startswith(version):
        result = db.query(table).filter(table.c.mask == mask).order_by(table.c.timestamp.desc()).first()
        if result:
            db.execute(table.update().values(version = content).where(table.c.timestamp == result[0]).where(mask == mask))
            db.commit()
