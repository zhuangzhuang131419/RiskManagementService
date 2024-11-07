import { DetailsList, DetailsListLayoutMode, SelectionMode, Stack, Text } from '@fluentui/react';
import { TopBarData } from '../Model/User';
import { isVisible } from '@testing-library/user-event/dist/utils';
import { useQuery } from 'react-query';
import { optionDataProvider } from '../DataProvider/OptionDataProvider';
import { CashGreeksResponse } from '../Model/OptionData';
import { useEffect, useState } from 'react';

interface TopDataBarProps {
  indexSymbol: string
  etfSymbol: string
}




const TopDataBar: React.FC<TopDataBarProps> = ({ indexSymbol, etfSymbol }) => {

  const [items, setItems] = useState<any[]>([]);


  const { data: indexData } = useQuery(
    ['cashGreeks', indexSymbol],  // symbol 作为查询的 key，symbol 变化时会重新加载
    () => optionDataProvider.fetchCashGreeks(indexSymbol as string),
    {
      onSuccess(data) {
      },
      refetchInterval: 3000, // 每隔 3 秒重新获取一次数据
      enabled: !!indexSymbol,  // 只有当 symbol 存在时才启用查询
      refetchOnWindowFocus: false, // 禁用在窗口获得焦点时重新获取数据
    }
  );

  const { data: etfData } = useQuery(
    ['cashGreeks', indexSymbol],  // symbol 作为查询的 key，symbol 变化时会重新加载
    () => optionDataProvider.fetchCashGreeks(etfSymbol as string),
    {
      onSuccess(data) {
      },
      refetchInterval: 3000, // 每隔 3 秒重新获取一次数据
      enabled: !!indexSymbol,  // 只有当 symbol 存在时才启用查询
      refetchOnWindowFocus: false, // 禁用在窗口获得焦点时重新获取数据
    }
  );

  useEffect(() => {
    const defaultCashGreeks: CashGreeksResponse = {
      delta: null,
      delta_cash: null,
      gamma_p_cash: null,
      vega_cash: null,
      db_cash: null,
      vanna_vs_cash: null,
      vanna_sv_cash: null,
      charm_cash: null,
    };

    const combinedData = [
      indexData
        ? { type: "指数期权", ...indexData }
        : { type: "指数期权", defaultCashGreeks },
      etfData
        ? { type: "ETF期权", ...etfData }
        : { type: "ETF期权", defaultCashGreeks },
      { type: "期货", defaultCashGreeks },
      { type: "综合", defaultCashGreeks }
    ];
    setItems(combinedData);
  }, [indexData, etfData]);


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
