import { DetailsList, DetailsListLayoutMode, SelectionMode, Stack, Text } from '@fluentui/react';
import { TopBarData } from '../Model/User';
import { isVisible } from '@testing-library/user-event/dist/utils';
import { useQuery } from 'react-query';
import { optionDataProvider } from '../DataProvider/OptionDataProvider';
import { CashGreeksResponse } from '../Model/OptionData';
import { useState } from 'react';

interface TopDataBarProps {
  symbol: string
}




const TopDataBar: React.FC<TopDataBarProps> = ({ symbol }) => {

  const [items, setItems] = useState<CashGreeksResponse[]>([]);


  const { data, isLoading, isError } = useQuery(
    ['cashGreeks', symbol],  // symbol 作为查询的 key，symbol 变化时会重新加载
    () => optionDataProvider.fetchCashGreeks(symbol as string),
    {
      onSuccess(data) {
        const processedData = [
          { type: "指数期权", ...data[0] },
          { type: "ETF期权", ...data[1] },
          { type: "期货", ...data[2] }
        ];
        setItems(processedData)
      },
      refetchInterval: 3000, // 每隔 3 秒重新获取一次数据
      enabled: !!symbol,  // 只有当 symbol 存在时才启用查询
      refetchOnWindowFocus: false, // 禁用在窗口获得焦点时重新获取数据
    }
  );

  // Handle loading state
  if (isLoading) return <div>Loading...</div>;

  // Handle error state
  if (isError) return <div>Error: fetchCashGreeks</div>;



  const columns = [
    { key: 'type', name: '类型', fieldName: 'type', minWidth: 100, maxWidth: 150, isResizable: true },
    { key: 'delta', name: 'Delta', fieldName: 'delta', minWidth: 100, maxWidth: 150, isResizable: true },
    { key: 'delta_cash', name: 'Delta Cash', fieldName: 'delta_cash', minWidth: 100, maxWidth: 150, isResizable: true },
    { key: 'gamma_p_cash', name: 'GammaP Cash', fieldName: 'gamma_p_cash', minWidth: 100, maxWidth: 150, isResizable: true },
    { key: 'vega_cash', name: 'Vega Cash', fieldName: 'vega_cash', minWidth: 100, maxWidth: 150, isResizable: true },
    { key: 'db_cash', name: 'Db Cash', fieldName: 'db_cash', minWidth: 100, maxWidth: 150, isResizable: true },
    { key: 'vanna_vs_cash', name: 'VannaVS Cash', fieldName: 'vanna_vs_cash', minWidth: 100, maxWidth: 150, isResizable: true },
    { key: 'vanna_sv_cash', name: 'VannaSV Cash', fieldName: 'vanna_sv_cash', minWidth: 100, maxWidth: 150, isResizable: true },
    { key: 'charm_cash', name: 'Charm Cash', fieldName: 'charm_cash', minWidth: 100, maxWidth: 150, isResizable: true },
  ];

  return (
    <DetailsList
      items={items}
      layoutMode={DetailsListLayoutMode.fixedColumns}
      selectionMode={SelectionMode.none}
      columns={columns}
      isHeaderVisible={true}
    />
  );
};

export default TopDataBar;
