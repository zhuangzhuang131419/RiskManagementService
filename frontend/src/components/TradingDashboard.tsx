import React, { useEffect, useState } from 'react';
import { ChoiceGroup, Stack, IChoiceGroupOption, Dialog, Label, Text } from '@fluentui/react';
import OptionGreeks from './OptionGreeks';
import { QueryClient, QueryClientProvider, useQuery } from 'react-query';
import UserSelector from './UserSelector';
import ScrollBox from './ScrollBox';
import { optionDataProvider } from '../DataProvider/OptionDataProvider';
import TopDataBar from './TopDataBar';
import { User, TopBarData } from '../Model/User';
import { futureDataProvider } from '../DataProvider/FutureDataProvider';
import { userDataProvider } from '../DataProvider/UserDataProvider';
import WingModelBar from './WingModelBar';
import { WingModelData } from '../Model/OptionData';
import BaselineSelector from './BaselineSelector';
import CustomizedParaDialog from './CustomizedParaDialog';
import UserInfoTable from './UserInfoTable';

const stackStyles = {
    root: {
        width: '100%',
        marginTop: '20px',
    },
};

document.body.style.overflow = 'hidden';
document.documentElement.style.overflow = 'hidden';

const TradingDashboard: React.FC = () => {
    const [selectedUserKey, setSelectedUserKey] = useState<string | null>(null);
    const [selectedIndexOption, setSelectedIndexOption] = useState<string | null>(null);
    const [selectedFuture, setSelectedFuture] = useState<string | null>(null);
    const [selectedETFOption, setSelectedETF] = useState<string | null>(null);
    const [selectedBaseline, setSelectedBaseline] = useState<string>();
    const [clock, setClock] = useState<string>();

    const { data: userItems, isFetching: isUserFetching } = useQuery(
        ['users'],
        userDataProvider.fetchUsers,
    );

    const { data } = useQuery(
        ['clock'],
        userDataProvider.fetchClock,
        {
            onSuccess(data) {
                setClock(data);
            },
            refetchInterval: 3000,
        }
    );

    const { data: indexOptionItems, isFetching: isIndexOptionFetching } = useQuery(
        ['indexOptions'],
        optionDataProvider.fetchIndexOptionSymbols,
        {
            select(data) {
                return data.map((item) => ({ key: item }))
            },
            onSuccess(data) {
                console.log('fetchIndexOptionSymbols:' + data)
            },
        }
    );

    const { data: etfOptionItems, isFetching: isETFOptionFetching } = useQuery(
        ['etfOptions'],
        optionDataProvider.fetchETFOptionSymbols,
        {
            select(data) {
                return data.map((item) => ({ key: item }))
            },
            onSuccess(data) {
                console.log('fetchETFOptionSymbols:' + data)
            },
        }
    );

    return (

        // 主布局
        <Stack tokens={{ childrenGap: 20 }} styles={{ root: { height: '100vh', width: '100vw' } }}>
            {/* 顶部：账户选择器和数据展示 */}
            <Stack horizontal styles={{ root: { height: '20%' } }} tokens={{ childrenGap: 20 }}>
                <Stack.Item>
                    {!isUserFetching && (
                        <UserSelector accounts={userItems as User[]} onSelect={setSelectedUserKey} selectedUserKey={selectedUserKey} />
                    )}
                    <Text>{clock}</Text>
                </Stack.Item>
                <Stack.Item>
                    <UserInfoTable></UserInfoTable>
                </Stack.Item>
                <Stack.Item>
                    {selectedUserKey !== null && (
                        <TopDataBar indexSymbol={selectedIndexOption as string} etfSymbol={selectedETFOption as string} />
                    )}
                </Stack.Item>
            </Stack>



            {/* 中间部分：期权滚动框和期权希腊字母展示 */}
            <Stack horizontal styles={{ root: { height: '80%' } }} tokens={{ childrenGap: 20 }}>
                {/* 左侧：ScrollBox */}
                <Stack tokens={{ childrenGap: 10 }} styles={{ root: { width: '15%' } }}>
                    {!isIndexOptionFetching && (
                        <Stack styles={{ root: { height: '30%' } }}>
                            <ScrollBox
                                items={indexOptionItems as { key: string }[]}
                                onClick={setSelectedIndexOption}
                                renderItem={(item) => {
                                    const prefix = item.key.slice(0, item.key.length - 8);
                                    const year = item.key.slice(item.key.length - 6, item.key.length - 4);
                                    const month = item.key.slice(item.key.length - 4, item.key.length - 2);
                                    return `${prefix}${year}${month}`;
                                }}
                                title='指数期权'
                                selectedItemKey={selectedIndexOption}
                            />
                        </Stack>
                    )}
                    {!isETFOptionFetching && (
                        <Stack styles={{ root: { height: '30%' } }}>
                            <ScrollBox
                                items={etfOptionItems as { key: string }[]}
                                onClick={setSelectedETF}
                                renderItem={(item) => {
                                    const prefix = item.key.slice(0, item.key.length - 8);
                                    const year = item.key.slice(item.key.length - 6, item.key.length - 4);
                                    const month = item.key.slice(item.key.length - 4, item.key.length - 2);
                                    return `${prefix}-${year}${month}`;
                                }}
                                title='ETF期权'
                                selectedItemKey={selectedETFOption}
                            />
                        </Stack>
                    )}
                    <Stack styles={{ root: { height: '20%', overflowY: 'auto' } }}>
                        <BaselineSelector
                            onSelect={setSelectedBaseline}
                            selectedBaselineKey={selectedBaseline as string}
                        />
                    </Stack>
                    <Stack styles={{ root: { height: '20%', overflowY: 'auto' } }}>
                        <CustomizedParaDialog></CustomizedParaDialog>
                    </Stack>
                </Stack>

                {/* 右侧：OptionGreeks */}
                <Stack horizontal styles={{ root: { height: '100%', width: '85%' } }} tokens={{ childrenGap: 10 }}>
                    <Stack tokens={{ childrenGap: 10 }} styles={{ root: { width: '50%' } }}>
                        <WingModelBar symbol={selectedIndexOption} style={{ height: '20%' }} />
                        <OptionGreeks symbol={selectedIndexOption} style={{ overflowY: 'auto', height: '90%' }} />
                    </Stack>
                    <Stack tokens={{ childrenGap: 10 }} styles={{ root: { width: '50%' } }}>
                        <WingModelBar symbol={selectedETFOption} style={{ height: '20%' }} />
                        <OptionGreeks symbol={selectedETFOption} style={{ overflowY: 'auto', height: '90%' }} />
                    </Stack>
                </Stack>
            </Stack>
        </Stack>
    )
};

export default TradingDashboard;
