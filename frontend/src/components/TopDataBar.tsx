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

  const { data: futureData } = useQuery(
    ['futureGreeks', indexSymbol],  // symbol 作为查询的 key，symbol 变化时会重新加载
    () => optionDataProvider.fetchFutureGreeksSummary(indexSymbol as string),
    {
      onSuccess(data) {
        console.log('fetchFutureGreeksSummary:' + indexSymbol + "-" + JSON.stringify(data))
      },
      refetchInterval: 3000, // 每隔 3 秒重新获取一次数据
      enabled: !!indexSymbol,  // 只有当 symbol 存在时才启用查询
      refetchOnWindowFocus: false, // 禁用在窗口获得焦点时重新获取数据
    }
  );


  const { data: indexData } = useQuery(
    ['indexOptionGreeks', indexSymbol],  // symbol 作为查询的 key，symbol 变化时会重新加载
    () => optionDataProvider.fetchOptionGreeksSummary(indexSymbol as string),
    {
      onSuccess(data) {
        console.log('fetchOptionGreeksSummary' + indexSymbol + "-" + JSON.stringify(data))
      },
      refetchInterval: 3000, // 每隔 3 秒重新获取一次数据
      enabled: !!indexSymbol,  // 只有当 symbol 存在时才启用查询
      refetchOnWindowFocus: false, // 禁用在窗口获得焦点时重新获取数据
    }
  );

  const { data: etfData } = useQuery(
    ['etfOptionGreeks', etfSymbol],  // symbol 作为查询的 key，symbol 变化时会重新加载
    () => optionDataProvider.fetchOptionGreeksSummary(etfSymbol as string),
    {
      onSuccess(data) {
        console.log('fetchOptionGreeksSummary' + JSON.stringify(data))
      },
      refetchInterval: 3000, // 每隔 3 秒重新获取一次数据
      enabled: !!etfSymbol,  // 只有当 symbol 存在时才启用查询
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
      underlying_price: null,
    };

    const sumCashGreeks = (index: CashGreeksResponse, etf: CashGreeksResponse, future: CashGreeksResponse) => {
      const result: CashGreeksResponse = { ...defaultCashGreeks };

      // Use 'keyof CashGreeksResponse' to iterate over valid keys
      for (const key of Object.keys(result) as Array<keyof CashGreeksResponse>) {
        if (key === "delta") {
          result[key] = (index[key] ?? 0) + (etf[key] ?? 0) / 10 + (future[key] ?? 0) * 3;
        } else {
          result[key] = (index[key] ?? 0) + (etf[key] ?? 0) + (future[key] ?? 0);
        }

      }

      return result;
    };

    const combinedData = [
      indexData
        ? { type: "指数期权", ...indexData }
        : { type: "指数期权", defaultCashGreeks },
      etfData
        ? { type: "ETF期权", ...etfData }
        : { type: "ETF期权", defaultCashGreeks },
      futureData
        ? { type: "期货", ...futureData }
        : { type: "期货", defaultCashGreeks },
      {
        type: "综合",
        ...sumCashGreeks(
          indexData || defaultCashGreeks,
          etfData || defaultCashGreeks,
          futureData || defaultCashGreeks
        )
      }
    ];
    setItems(combinedData);
  }, [indexData, etfData, futureData]);

  const formatPercentage = (value: number | null): string =>
    value !== null && !isNaN(value) ? `${(value).toFixed(2)}` : '--';


  const columns = [
    { key: 'type', name: '类型', fieldName: 'type', minWidth: 100, maxWidth: 150, isResizable: true },
    {
      key: 'delta',
      name: 'Delta',
      fieldName: 'delta',
      minWidth: 100,
      maxWidth: 150,
      isResizable: true,
      onRender: (item: CashGreeksResponse) => <span>{formatPercentage(item.delta)}</span>,
    },
    {
      key: 'delta_cash',
      name: 'Delta Cash',
      fieldName: 'delta_cash',
      minWidth: 100,
      maxWidth: 150,
      isResizable: true,
      onRender: (item: CashGreeksResponse) => <span>{formatPercentage(item.delta_cash)}</span>,
    },
    {
      key: 'gamma_p_cash',
      name: 'GammaP Cash',
      fieldName: 'gamma_p_cash',
      minWidth: 100,
      maxWidth: 150,
      isResizable: true,
      onRender: (item: CashGreeksResponse) => <span>{formatPercentage(item.gamma_p_cash)}</span>,
    },
    {
      key: 'vega_cash',
      name: 'Vega Cash',
      fieldName: 'vega_cash',
      minWidth: 100,
      maxWidth: 150,
      isResizable: true,
      onRender: (item: CashGreeksResponse) => <span>{formatPercentage(item.vega_cash)}</span>,
    },
    {
      key: 'db_cash',
      name: 'Db Cash',
      fieldName: 'db_cash',
      minWidth: 100,
      maxWidth: 150,
      isResizable: true,
      onRender: (item: CashGreeksResponse) => <span>{formatPercentage(item.db_cash)}</span>,
    },
    {
      key: 'vanna_vs_cash',
      name: 'VannaVS Cash',
      fieldName: 'vanna_vs_cash',
      minWidth: 100,
      maxWidth: 150,
      isResizable: true,
      onRender: (item: CashGreeksResponse) => <span>{formatPercentage(item.vanna_vs_cash)}</span>,
    },
    {
      key: 'vanna_sv_cash',
      name: 'VannaSV Cash',
      fieldName: 'vanna_sv_cash',
      minWidth: 100,
      maxWidth: 150,
      isResizable: true,
      onRender: (item: CashGreeksResponse) => <span>{formatPercentage(item.vanna_sv_cash)}</span>,
    },
    {
      key: 'charm_cash',
      name: 'Charm Cash',
      fieldName: 'charm_cash',
      minWidth: 100,
      maxWidth: 150,
      isResizable: true,
      onRender: (item: CashGreeksResponse) => <span>{formatPercentage(item.charm_cash)}</span>,
    },
    {
      key: 'underlying_price',
      name: 'S',
      fieldName: 'underlying_price',
      minWidth: 100,
      maxWidth: 150,
      isResizable: true,
      onRender: (item: CashGreeksResponse) => <span>{formatPercentage(item.underlying_price)}</span>,
    },
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
