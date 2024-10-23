import React, { useState } from 'react';
import { Stack } from '@fluentui/react';
import OptionGreeks from './OptionGreeks';
import { QueryClient, QueryClientProvider, useQuery } from 'react-query';
import AccountSelector from './AccountSelector';
import ScrollBox from './ScrollBox';
import { symbolName } from 'typescript';
import { optionDataProvider } from '../DataProvider/OptionDataProvider';
import TopDataBar from './TopDataBar';
import { TopBarData } from '../Model/Account';
import { futureDataProvider } from '../DataProvider/FutureDataProvider';

const stackStyles = {
    root: {
        width: '100%',
        marginTop: '20px',
    },
};

document.body.style.overflow = 'hidden';
document.documentElement.style.overflow = 'hidden';




const TradingDashboard: React.FC = () => {
    const [selectedAccount, setSelectedAccount] = useState<string>("account1");
    const [selectedOption, setSelectedOption] = useState<string | null>(null);
    const [selectedFuture, setSelectedFuture] = useState<string | null>(null);

    const accounts = [
        {
            name: "账户一",
            id: "account1"
        },
        {
            name: "账户二",
            id: "account2"
        }
    ];

    const { data: optionItems, isFetching: isOptionFetching } = useQuery(
        ['options'],
        optionDataProvider.fetchOptionSymbols,
    );

    const { data: futureItems, isFetching: isFutureFetching } = useQuery(
        ['futures'],
        futureDataProvider.fetchFutureSymbols,
    );

    // console.log("optionItems" + optionItems)

    const topBarData: TopBarData = {
        greekLetters: {
            delta: 0.5,
            vega: 0.3,
            theta: -0.1,
        },
        indexOptionCount: 120,
        etfOptionCount: 80,
        futureCount: 50,
        cashCombined: 1000000,
    };

    return (
        // 主布局
        <Stack tokens={{ childrenGap: 20 }} styles={{ root: { height: '90vh', width: '100%' } }}>
            {/* 顶部：账户选择器和数据展示 */}
            <Stack horizontal tokens={{ childrenGap: 20 }} styles={{ root: { alignItems: 'center' } }}>
                <Stack.Item grow={1}>
                    <AccountSelector accounts={accounts} onSelect={setSelectedAccount} />
                </Stack.Item>
                <Stack.Item grow={2}>
                    <TopDataBar data={topBarData} />
                </Stack.Item>
            </Stack>

            {/* 中间部分：期权滚动框和期权希腊字母展示 */}
            <Stack horizontal tokens={{ childrenGap: 20 }} styles={{ root: { height: '100%' } }}>
                {/* 左侧：ScrollBox */}
                <Stack tokens={{ childrenGap: 10 }} styles={{ root: { width: '15%' } }}>
                    {!isOptionFetching && (
                        <ScrollBox
                            items={optionItems as string[]}
                            onClick={setSelectedOption}
                            renderItem={(item) => item as string}
                        />
                    )}
                    {!isFutureFetching && (
                        <ScrollBox
                            items={futureItems as string[]}
                            onClick={setSelectedFuture}
                            renderItem={(item) => item as string}
                        />
                    )}
                </Stack>

                {/* 右侧：OptionGreeks */}
                <Stack horizontal tokens={{ childrenGap: 10 }} grow={1} styles={{ root: { height: '100%' }}}>
                    <OptionGreeks symbol={selectedOption} />
                    <OptionGreeks symbol={selectedOption} />
                </Stack>
            </Stack>
        </Stack>
    )
};

export default TradingDashboard;
