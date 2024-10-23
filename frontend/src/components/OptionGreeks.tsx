import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { Stack, DetailsList, IColumn, Text } from '@fluentui/react';
import { optionDataProvider } from '../DataProvider/OptionDataProvider';

interface OptionGreeksProps {
    symbol: string | null;
}

const OptionGreeks: React.FC<OptionGreeksProps> = ({ symbol }) => {

    const [items, setItems] = useState<any[]>([]);

    // 使用 useQuery 自动管理数据获取，每当 symbol 变化时重新加载
    const { data: greeksData, error, isLoading } = useQuery(
        ['greeks', symbol],  // symbol 作为查询的 key，symbol 变化时会重新加载
        () => optionDataProvider.fetchOptionGreeks(symbol as string),  // 数据获取函数
        {
            onSuccess(data) {
                const formattedItems = Object.keys(data.strike_prices).map((strikePrice) => {
                    const strikeData = data.strike_prices[strikePrice];
                    console.log('Response data: ', strikeData);
                    return {
                        strikePrice, // 行权价格
                        callDelta: strikeData.call_option.delta,
                        callGamma: strikeData.call_option.gamma,
                        callVega: strikeData.call_option.vega,
                        callTheta: strikeData.call_option.theta,
                        putDelta: strikeData.put_option.delta,
                        putGamma: strikeData.put_option.gamma,
                        putVega: strikeData.put_option.vega,
                        putTheta: strikeData.put_option.theta,
                    };
                });

                setItems(formattedItems); // 更新表格项
            },
            refetchInterval: 3000, // 每隔 3 秒重新获取一次数据
            enabled: !!symbol,  // 只有当 symbol 存在时才启用查询
            refetchOnWindowFocus: false, // 禁用在窗口获得焦点时重新获取数据
        }
    );

    if (isLoading) {
        return <Text>Loading Greeks data...</Text>;
    }

    if (error) {
        return <Text>Error loading Greeks data</Text>;
    }

    if (!greeksData) {
        return <Text>No Greeks data available for {symbol}</Text>;
    }

    // 设置列
    const columns: IColumn[] = [
        
        { key: 'callDelta', name: 'Call Delta', fieldName: 'callDelta', minWidth: 10, maxWidth: 80, isResizable: true },
        { key: 'callGamma', name: 'Call Gamma', fieldName: 'callGamma', minWidth: 10, maxWidth: 80, isResizable: true },
        { key: 'callVega', name: 'Call Vega', fieldName: 'callVega', minWidth: 10, maxWidth: 80, isResizable: true },
        { key: 'callTheta', name: 'Call Theta', fieldName: 'callTheta', minWidth: 10, maxWidth: 80, isResizable: true },
        { key: 'strikePrice', name: 'Strike Price', fieldName: 'strikePrice', minWidth: 10, maxWidth: 80, isResizable: true },
        { key: 'putDelta', name: 'Put Delta', fieldName: 'putDelta', minWidth: 10, maxWidth: 80, isResizable: true },
        { key: 'putGamma', name: 'Put Gamma', fieldName: 'putGamma', minWidth: 10, maxWidth: 80, isResizable: true },
        { key: 'putVega', name: 'Put Vega', fieldName: 'putVega', minWidth: 10, maxWidth: 80, isResizable: true },
        { key: 'putTheta', name: 'Put Theta', fieldName: 'putTheta', minWidth: 10, maxWidth: 80, isResizable: true },
    ];

    const scrollBoxStyles = {
        root: {
            height: '100%',   // 固定高度
            overflowX: 'hidden', // 禁用水平滚动
            overflowY: 'auto', // 垂直滚动
            // border: '1px solid #ccc', // 可选：添加边框
            // padding: '10px',   // 内边距
        },
    };

    return (
        <Stack tokens={{ childrenGap: 15 }}>
            <Text variant="large">Greeks for {symbol}</Text>
            <DetailsList
                items={items}
                columns={columns}
                setKey="set"
                layoutMode={0} // 默认布局
                styles={scrollBoxStyles}
            />
        </Stack>
    );
};

export default OptionGreeks;