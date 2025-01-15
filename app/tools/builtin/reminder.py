import asyncio
import datetime
from typing import Dict, Any
from app.agent import Agent
import logging

# 工具元数据
metadata = type('metadata', (), {
    'enable': True,
    'name': 'reminder',
    'description': '设置定时提醒，在指定时间向agent发送消息',
    'parameters': {
        'type': 'object',
        'properties': {
            'time': {
                'type': 'string',
                'format': 'date-time',
                'description': '提醒时间，ISO 8601格式'
            },
            'message': {
                'type': 'string',
                'description': '提醒消息内容'
            }
        },
        'required': ['time', 'message']
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

# 全局定时任务存储
reminder_tasks = {}

async def set_reminder(time: str, message: str) -> Dict[str, Any]:
    """设置定时提醒"""
    try:
        # 解析时间
        reminder_time = datetime.datetime.fromisoformat(time)
        now = datetime.datetime.now()
        
        # 计算延迟时间
        delay = (reminder_time - now).total_seconds()
        if delay <= 0:
            return {'status': 'error', 'message': '提醒时间不能是过去时间'}
            
        # 创建定时任务
        task = asyncio.create_task(_send_reminder(delay, message))
        reminder_tasks[time] = task
        
        return {'status': 'success', 'message': f'已设置提醒，将在{reminder_time}发送消息'}
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

async def _send_reminder(delay: float, message: str):
    """发送提醒消息"""
    await asyncio.sleep(delay)
    
    # 获取agent实例并发送消息
    agent = Agent.get_agent('default')
    await agent.think_once([{
        'role': 'system',
        'content': f'定时提醒：{message}'
    }])
    
    logging.info(f'已发送定时提醒：{message}')

# 导出工具函数
exports = {
    'set_reminder': set_reminder
}
