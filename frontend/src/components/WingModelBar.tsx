import { Callout, DefaultButton, DetailsList, SelectionMode, Stack, Text, Toggle } from '@fluentui/react';
import { WingModelData } from '../Model/OptionData';
import { useQuery } from 'react-query';
import { optionDataProvider } from '../DataProvider/OptionDataProvider';
import React, { useState, useEffect } from 'react';
import CustomizedModel from './CustomizedParaDialog';

interface WingModelProps {
  symbol: string | null;
}


const WingModelBar: React.FC<WingModelProps> = ({ symbol }) => {

  const [items, setItems] = useState<WingModelData[]>([]);

  const { data: wingModel, error, isLoading } = useQuery(
    ['wingModel', symbol],
    () => optionDataProvider.fetchWingModelParaBySymbol(symbol as string),
    {
      onSuccess(data) {
        console.log('fetchWingModelParaBySymbol' + JSON.stringify(data))
        setItems(data); // 更新表格项
      },
      refetchInterval: 3000, // 每隔 3 秒重新获取一次数据
      enabled: !!symbol,  // 只有当 symbol 存在时才启用查询
    }
  );

  if (isLoading) {
    return <Text>Loading wing model data...</Text>;
  }

  if (error) {
    return <Text>Error wing model data</Text>;
  }


  const scrollBoxStyles = {
    root: {
      height: '100%',
      width: '100%',
      overflowX: 'hidden', // 禁用水平滚动
      overflowY: 'hidden', // 禁用滚动
    },
  };

  const formatPercentage = (value: number | null): string =>
    value !== null && !isNaN(value) ? `${(value * 100).toFixed(2)}%` : '--';

  const columns = [
    {
      key: 'atmVol', name: 'ATM波动率', fieldName: 'atm_vol', minWidth: 100, maxWidth: 150, isResizable: true,
      onRender: (item: WingModelData) => <span>{formatPercentage(item.atm_vol)}</span>
    },
    {
      key: 'k1', name: 'K1', fieldName: 'k1', minWidth: 100, maxWidth: 150, isResizable: true,
      onRender: (item: WingModelData) => <span>{formatPercentage(item.k1)}</span>
    },
    {
      key: 'k2', name: 'K2', fieldName: 'k2', minWidth: 100, maxWidth: 150, isResizable: true,
      onRender: (item: WingModelData) => <span>{formatPercentage(item.k2)}</span>
    },
    {
      key: 'b', name: 'b', fieldName: 'b', minWidth: 100, maxWidth: 150, isResizable: true,
      onRender: (item: WingModelData) => <span>{formatPercentage(item.b)}</span>
    },
    {
      key: 'atmAvailable', name: 'ATM 可用性', fieldName: 'atm_available', minWidth: 100, maxWidth: 150, isResizable: true,
      onRender: (item: WingModelData) => <span>{item.atm_available ? 'Yes' : 'No'}</span>
    },
  ];

  return (
    <DetailsList
      items={items}
      selectionMode={SelectionMode.none}
      columns={columns}
      styles={scrollBoxStyles}
    />
  );
};

export default WingModelBar;
