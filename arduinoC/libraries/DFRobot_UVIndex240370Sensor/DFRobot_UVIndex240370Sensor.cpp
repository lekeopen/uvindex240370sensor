/*!
 * @file DFRobot_UVIndex240370Sensor.cpp
 * @brief This is the method implementation file of UVIndex240370Sensor
 * @copyright   Copyright (c) 2010 DFRobot Co.Ltd (http://www.dfrobot.com)
 * @license     The MIT License (MIT)
 * @author [fary](feng.yang@dfrobot.com)
 * @version  V0.1.0
 * @date  2025-05-14
 * @url https://github.com/lekeopen/uvindex240370sensor
 */

#include "DFRobot_UVIndex240370Sensor.h"

DFRobot_UVIndex240370Sensor::DFRobot_UVIndex240370Sensor(TwoWire *pWire)
{
  _pWire = pWire;
};

DFRobot_UVIndex240370Sensor::DFRobot_UVIndex240370Sensor(Stream *s) : DFRobot_RTU(s)
{
  _s = s;
}

bool DFRobot_UVIndex240370Sensor::begin(void)
{
  setTimeoutTimeMs(200);
  bool ret = false;
  if (_pWire)
  {
    _pWire->begin();
    _pWire->beginTransmission(_addr);
    if (_pWire->endTransmission() == 0)
    {
      ret = true;
    }
  }
  else
  {
    uint8_t buffer[2];
    readReg(0x00, buffer, 2);
    uint16_t data = (uint16_t)buffer[0] << 8 | buffer[1];
    if (data == UVINDEX240370SENSOR_DEVICE_PID)
    {
      ret = true;
    }
  }
  return ret;
}

uint16_t DFRobot_UVIndex240370Sensor::readUvOriginalData(void)
{
  uint8_t buffer[2];
  readReg(UVINDEX240370SENSOR_INPUTREG_UVS_DATA, buffer, 2);
  uint16_t data = (uint16_t)buffer[0] << 8 | buffer[1];
  return data;
}

uint16_t DFRobot_UVIndex240370Sensor::readUvIndexData(void)
{
  // 获取原始UV值
  uint16_t rawValue = readUvOriginalData();

  // 对原始值进行映射计算UV指数
  // 小于100的值映射为0
  // 参考UV指数标准: 0-2低风险，3-5中等风险，6-7高风险，8-10极高风险，11+极端风险
  uint16_t uvIndex;

  if (rawValue < 50)
  {              // 将阈值从100调整为50，与Python版本保持一致
    uvIndex = 0; // 非常小的值视为UV指数0
  }
  else if (rawValue < 227)
  {              // 将阈值从200调整为227，与Python版本保持一致
    uvIndex = 1; // 较小的值视为UV指数1
  }
  else if (rawValue < 318)
  {              // 将阈值从400调整为318，与Python版本保持一致
    uvIndex = 2; // 适中的值视为UV指数2
  }
  else if (rawValue < 408)
  {
    uvIndex = 3; // UV指数3
  }
  else if (rawValue < 503)
  {
    uvIndex = 4; // UV指数4
  }
  else if (rawValue < 606)
  {
    uvIndex = 5; // UV指数5
  }
  else if (rawValue < 696)
  {
    uvIndex = 6; // UV指数6
  }
  else if (rawValue < 795)
  {
    uvIndex = 7; // UV指数7
  }
  else if (rawValue < 881)
  {
    uvIndex = 8; // UV指数8
  }
  else if (rawValue < 976)
  {
    uvIndex = 9; // UV指数9
  }
  else if (rawValue < 1079)
  {
    uvIndex = 10; // UV指数10
  }
  else
  {
    uvIndex = 11; // 超过1079的值视为UV指数11
  }

  return uvIndex;
}
uint16_t DFRobot_UVIndex240370Sensor::readRiskLevelData(void)
{
  // 获取我们计算后的UV指数
  uint16_t uvIndex = readUvIndexData();

  // 根据UV指数计算风险级别
  // 0-2: 低风险(0)
  // 3-5: 中等风险(1)
  // 6-7: 高风险(2)
  // 8-10: 非常高风险(3)
  // 11+: 极端风险(4)
  uint16_t riskLevel;

  if (uvIndex < 3)
  {
    riskLevel = 0; // 低风险
  }
  else if (uvIndex < 6)
  {
    riskLevel = 1; // 中等风险
  }
  else if (uvIndex < 8)
  {
    riskLevel = 2; // 高风险
  }
  else if (uvIndex < 11)
  {
    riskLevel = 3; // 非常高风险
  }
  else
  {
    riskLevel = 4; // 极端风险
  }

  return riskLevel;
}

uint8_t DFRobot_UVIndex240370Sensor::readReg(uint16_t reg, void *pBuf, uint8_t size)
{
  uint8_t *_pBuf = (uint8_t *)pBuf;
  uint8_t _reg = 0;
  if (pBuf == NULL)
  {
    DBG("data error");
    return 0;
  }
  if (_pWire)
  {
    _pWire->beginTransmission(_addr);
    _pWire->write(reg);
    _pWire->endTransmission();
    _pWire->requestFrom(_addr, size);
    for (uint8_t i = 0; i < size; i++)
      _pBuf[i] = _pWire->read();
    for (uint8_t i = 0; i < size;)
    {
      uint8_t temp = _pBuf[i];
      _pBuf[i] = _pBuf[i + 1];
      _pBuf[i + 1] = temp;
      i += 2;
    }
    return size;
  }
  else
  {
    return readInputRegister(_addr, reg, _pBuf, size);
  }
}
