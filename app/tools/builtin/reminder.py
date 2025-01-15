import asyncio
import datetime
from typing import Dict, Any
from app.core import EventManager
from app.agent import Agent
import logging
from dataclasses import dataclass

@dataclass
class AgentMessageEvent:
    """Agent间消息事件"""
    trigger_time: datetime.datetime
    from_agent: str
    to_agent: str
    message: str

# 工具元数据
metadata = type('metadata', (), {
    'enable': True,
    'name': 'reminder',
    'description': '设置定时提醒，在指定时间向目标agent发送消息',
    'parameters': {
        'type': 'object',
        'properties': {
            'time': {
                'type': 'string',
                'format': 'date-time',
                'description': '提醒时间，ISO 8601格式'
            },
            'from_agent': {
                'type': 'string',
                'description': '发送方agent名称'
            },
            'to_agent': {
                'type': 'string',
                'description': '接收方agent名称'
            },
            'message': {
                'type': 'string',
                'description': '提醒消息内容'
            }
        },
        'required': ['time', 'from_agent', 'to_agent', 'message']
    }
})

# 工具接口定义
tools = [{
    'type': 'function',
    'function': {
        'name': 'set_reminder',
        'description': '设置一个定时提醒',
        'parameters': metadata.parameters
    }
}]

async def set_reminder(time: str, from_agent: str, to_agent: str, message: str) -> Dict[str, Any]:
    """设置定时提醒"""
    try:
        # 解析时间
        trigger_time = datetime.datetime.fromisoformat(time)
        now = datetime.datetime.now()
        
        # 计算延迟时间
        delay = (trigger_time - now).total_seconds()
        if delay <= 0:
            return {'status': 'error', 'message': '提醒时间不能是过去时间'}
            
        # 创建事件
        event = AgentMessageEvent(
            trigger_time=trigger_time,
            from_agent=from_agent,
            to_agent=to_agent,
            message=message
        )
        
        # 创建定时任务
        asyncio.create_task(_schedule_event(delay, event))
        
        return {'status': 'success', 'message': f'已设置提醒，将在{trigger_time}发送消息'}
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

async def _schedule_event(delay: float, event: AgentMessageEvent):
    """调度事件"""
    await asyncio.sleep(delay)
    await EventManager.add_event(event)

@EventManager.register()
async def handle_agent_message(event: AgentMessageEvent):
    """处理Agent消息事件"""
    try:
        agent = Agent.get_agent(event.to_agent)
        response = await agent.think_once([{
            'role': 'system',
            'content': f'来自 {event.from_agent} 的定时提醒：{event.message}'
        }])
        
        # 将响应发送回源agent
        source_agent = Agent.get_agent(event.from_agent)
        await source_agent.think_once([{
            'role': 'system',
            'content': f'已向 {event.to_agent} 发送提醒，响应：{response}'
        }])
        
        logging.info(f'已处理Agent消息事件：{event}')
    except Exception as e:
        logging.error(f'处理Agent消息事件失败：{e}')

# 导出工具函数
exports = {
    'set_reminder': set_reminder
}
