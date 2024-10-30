import React, { useState } from 'react';
import { ChoiceGroup, Stack, IChoiceGroupOption } from '@fluentui/react';
import OptionGreeks from './OptionGreeks';
import { QueryClient, QueryClientProvider, useQuery } from 'react-query';
import AccountSelector from './AccountSelector';
import ScrollBox from './ScrollBox';
import { symbolName } from 'typescript';
import { optionDataProvider } from '../DataProvider/OptionDataProvider';
import TopDataBar from './TopDataBar';
import { Account, TopBarData } from '../Model/Account';
import { futureDataProvider } from '../DataProvider/FutureDataProvider';
import { userDataProvider } from '../DataProvider/UserDataProvider';
import WingModelBar from './WingModelBar';
import { WingModelData } from '../Model/OptionData';

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
    const [selectedIndexOption, setSelectedIndexOption] = useState<string | null>(null);
    const [selectedFuture, setSelectedFuture] = useState<string | null>(null);
    const [selectedETFOption, setSelectedETF] = useState<string | null>(null);

    const [selectedKey, setSelectedKey] = React.useState<string>('B'); // 设置默认选中 'B'

    const { data: userItems, isFetching: isUserFetching } = useQuery(
        ['users'],
        userDataProvider.fetchUsers,
        {
            select(data) {
                return data
            },
        }
    );

    const { data: indexOptionItems, isFetching: isIndexOptionFetching } = useQuery(
        ['indexOptions'],
        optionDataProvider.fetchIndexOptionSymbols,
        {
            onSuccess(data) {},
        }
    );

    const { data: futureItems, isFetching: isFutureFetching } = useQuery(
        ['futures'],
        futureDataProvider.fetchFutureSymbols,
    );

    const { data: etfOptionItems, isFetching: isETFOptionFetching } = useQuery(
        ['etfOptions'],
        optionDataProvider.fetchETFOptionSymbols,
    );

    

    // console.log("optionItems" + optionItems)

    const topBarData: TopBarData[] = [{
        greekLetters: {
            delta: 0.5,
            vega: 0.3,
            theta: -0.1,
        },
        indexOptionCount: 120,
        etfOptionCount: 80,
        futureCount: 50,
        cashCombined: 1000000,
    }];

    return (

        // 主布局
        <Stack tokens={{ childrenGap: 20 }} styles={{ root: { height: '90vh', width: '100%' } }}>
            {/* 顶部：账户选择器和数据展示 */}
            <Stack horizontal tokens={{ childrenGap: 20 }} styles={{ root: { alignItems: 'center' } }}>
                <Stack.Item grow={1}>
                    {!isUserFetching &&(
                        <AccountSelector accounts={userItems as Account[]} onSelect={setSelectedAccount} />
                    )}
                </Stack.Item>
                <Stack.Item grow={2}>
                    <TopDataBar data={topBarData} />
                </Stack.Item>
            </Stack>

            {/* 中间部分：期权滚动框和期权希腊字母展示 */}
            <Stack horizontal tokens={{ childrenGap: 20 }} styles={{ root: { height: '100%' } }}>
                {/* 左侧：ScrollBox */}
                <Stack tokens={{ childrenGap: 10 }} styles={{ root: { width: '15%' } }}>
                    {!isIndexOptionFetching && (
                        <Stack styles={{ root: { height: '30%' } }}>
                            <ScrollBox
                                items={indexOptionItems as string[]}
                                onClick={setSelectedIndexOption}
                                renderItem={(item) => item as string}
                                title='期权'
                            />
                        </Stack>
                    )}
                    {!isFutureFetching && (
                        <Stack styles={{ root: { height: '30%' } }}>
                            <ScrollBox
                                items={futureItems as string[]}
                                onClick={setSelectedFuture}
                                renderItem={(item) => item as string}
                                title='期货'
                            />
                        </Stack> 
                    )}
                    {!isETFOptionFetching && (
                        <Stack styles={{ root: { height: '30%' } }}>
                            <ScrollBox
                                items={etfOptionItems as string[]}
                                onClick={setSelectedETF}
                                renderItem={(item) => item as string}
                                title='ETF'
                            />
                        </Stack> 
                    )}
                </Stack>

                {/* 右侧：OptionGreeks */}
                <Stack horizontal tokens={{ childrenGap: 10 }} grow={1} styles={{ root: { height: '100%' }}}>
                    <Stack tokens={{ childrenGap: 10 }} styles={{ root: { flex: 1 }}}>
                        <WingModelBar symbol={selectedIndexOption} style={{ flex: '0 0 10%' }} exchange='cffex'/>
                        <OptionGreeks symbol={selectedIndexOption} style={{ flex: '1 1 auto', overflowY: 'auto', height: '90%' }} exchange='cffex'/>
                    </Stack>
                    <Stack tokens={{ childrenGap: 10 }} styles={{ root: { flex: 1 }}}>
                        <WingModelBar symbol={selectedETFOption} style={{ flex: '0 0 10%' }} exchange='se'/>
                        <OptionGreeks symbol={selectedETFOption} style={{ flex: '1 1 auto', overflowY: 'auto', height: '90%' }} exchange='se'/>
                    </Stack>
                </Stack>
            </Stack>
        </Stack>
    )
};

export default TradingDashboard;
