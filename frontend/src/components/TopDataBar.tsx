import { DetailsList, DetailsListLayoutMode, SelectionMode, Stack, Text } from '@fluentui/react';
import { TopBarData } from '../Model/User';
import { isVisible } from '@testing-library/user-event/dist/utils';
import { useQuery } from 'react-query';
import { optionDataProvider } from '../DataProvider/OptionDataProvider';

interface TopDataBarProps {
  symbol: string
}




const TopDataBar: React.FC<TopDataBarProps> = ({ symbol }) => {

  const { data: greeksData, error, isLoading } = useQuery(
    ['cashGreeks', symbol],  // symbol 作为查询的 key，symbol 变化时会重新加载
    () => optionDataProvider.fetchOptionGreeks(symbol as string),
    {
      onSuccess(data) {
        const formattedItems = Object.keys(data.strike_prices).map((strikePrice) => {
          const strikeData = data.strike_prices[strikePrice];
          // console.log('Response data: ', strikeData);
          return {
            strikePrice, // 行权价格
            callDelta: strikeData.call_option.delta,
            callGamma: strikeData.call_option.gamma,
            callVega: strikeData.call_option.vega,
            callTheta: strikeData.call_option.theta,
            callVanna_sv: strikeData.call_option.vanna_sv,
            callVanna_vs: strikeData.call_option.vanna_vs,
            putDelta: strikeData.put_option.delta,
            putGamma: strikeData.put_option.gamma,
            putVega: strikeData.put_option.vega,
            putTheta: strikeData.put_option.theta,
            putVanna_sv: strikeData.put_option.vanna_sv,
            putVanna_vs: strikeData.put_option.vanna_vs,
          };
        });

        setItems(formattedItems); // 更新表格项
      },
      refetchInterval: 3000, // 每隔 3 秒重新获取一次数据
      enabled: !!symbol,  // 只有当 symbol 存在时才启用查询
      refetchOnWindowFocus: false, // 禁用在窗口获得焦点时重新获取数据
    }
  );



  const columns = [
    { key: 'metric', name: 'Metric', fieldName: 'metric', minWidth: 100, maxWidth: 150, isResizable: true, isVisible: false },
    { key: 'indexOption', name: '指数期权', fieldName: 'indexOption', minWidth: 100, maxWidth: 150, isResizable: true },
    { key: 'etfOption', name: 'Etf期权', fieldName: 'etfOption', minWidth: 100, maxWidth: 150, isResizable: true },
    { key: 'futures', name: '期货', fieldName: 'futures', minWidth: 100, maxWidth: 150, isResizable: true },
    { key: 'total', name: '综合', fieldName: 'total', minWidth: 100, maxWidth: 150, isResizable: true },
  ];

  // Define data rows based on the table
  const items = [
    { metric: 'Delta', indexOption: 1, etfOption: -1, futures: 2, total: '三者和' },
    { metric: 'Delta_cash', indexOption: '1*4001*100', etfOption: '-1*40020*1', futures: '2*4000*300', total: '三者和' },
    { metric: 'GammaP_cash', indexOption: -3000, etfOption: 2000, futures: 0, total: 0 },
    { metric: 'Vega_cash', indexOption: 0, etfOption: 0, futures: 0, total: 0 },
    { metric: 'Db_cash', indexOption: 0, etfOption: 0, futures: 0, total: 0 },
    { metric: 'VannaVS_cash', indexOption: 0, etfOption: 0, futures: 0, total: 0 },
    { metric: 'VannaSV_cash', indexOption: 0, etfOption: 0, futures: 0, total: 0 },
    { metric: 'Charm_cash', indexOption: 0, etfOption: 0, futures: 0, total: 0 },
    { metric: 'Dkurt_cash', indexOption: 0, etfOption: 0, futures: 0, total: 0 },
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
