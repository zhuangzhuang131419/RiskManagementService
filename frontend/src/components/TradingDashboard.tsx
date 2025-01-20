import React, { useEffect, useState } from 'react';
import { ChoiceGroup, Stack, IChoiceGroupOption, Dialog, Label, Text, Pivot, PivotItem, IDropdownOption, Dropdown } from '@fluentui/react';
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

    const [selectedIndexOption, setSelectedIndexOption] = useState<string | null>(null);
    const [selectedFuture, setSelectedFuture] = useState<string | null>(null);
    const [selectedETFOption, setSelectedETF] = useState<string | null>(null);
    const [selectedBaseline, setSelectedBaseline] = useState<string>();
    const [clock, setClock] = useState<string>();

    const { data: baseline } = useQuery<string>(
        ['baseline'],
        userDataProvider.fetchBaseline,
        {
            onSuccess(data) {
                if (selectedBaseline === null) {
                    setSelectedBaseline(data)
                }
            },
            refetchInterval: 1000 * 60 * 5
        }
    );

    const { data: userItems = [], isFetching: isUserFetching } = useQuery<User[]>(
        ['users'],
        userDataProvider.fetchUsers,
        {
            onSuccess(data) {
                if (selectedUserKey === null) {
                    setSelectedUserKey(data.length > 0 ? data[0].id : null)
                }
            },
            refetchInterval: 1000 * 60 * 5
        }
    );

    const [selectedUserKey, setSelectedUserKey] = useState<string | null>(null);

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

    const { data: indexOptionItems = [], isFetching: isIndexOptionFetching } = useQuery(
        ['indexOptions'],
        optionDataProvider.fetchIndexOptionSymbols,
        {
            select(data) {
                return data.map((item) => ({ key: item }))
            },
            onSuccess(data) {
                console.log('fetchIndexOptionSymbols:' + JSON.stringify(data))
            },
            refetchOnWindowFocus: false,
            refetchInterval: 1000 * 60 * 60,
        }

    );

    const { data: etfOptionItems = [], isFetching: isETFOptionFetching } = useQuery(
        ['etfOptions'],
        optionDataProvider.fetchETFOptionSymbols,
        {
            select(data) {
                return data.map((item) => ({ key: item }))
            },
            onSuccess(data) {
                console.log('fetchETFOptionSymbols:' + JSON.stringify(data))
            },

            refetchOnWindowFocus: false,
            refetchInterval: 1000 * 60 * 60,
        }
    );

    const [selectedGreek, setSelectedGreek] = useState<string>('cash_delta');

    // 希腊字母下拉框选项
    const greekOptions: IDropdownOption[] = [
        { key: 'cash_delta', text: 'Cash Delta' },
        { key: 'cash_vega', text: 'Cash Vega' },
        { key: 'cash_theta', text: 'Cash Theta' },
        { key: 'cash_GammaP', text: 'Cash GammaP' },
        { key: 'cash_db', text: 'Cash DB' },
        { key: 'cash_vannaVS', text: 'Cash VannaVS' },
        { key: 'cash_vannaSV', text: 'Cash VannaSV' },
        { key: 'cash_dkurt', text: 'Cash DKurt' },
    ];

    return (
        <Pivot>
            <PivotItem headerText='风控'>
                <Stack tokens={{ childrenGap: 20 }} styles={{ root: { height: '100vh', width: '100vw' } }}>
                    {/* 顶部：账户选择器和数据展示 */}
                    <Stack horizontal styles={{ root: { height: '20%' } }} tokens={{ childrenGap: 20 }}>
                        <Stack.Item>
                            {selectedUserKey !== null && (
                                <UserSelector accounts={userItems as User[]} onSelect={setSelectedUserKey} selectedUserKey={selectedUserKey} />
                            )}
                            <Text>{clock}</Text>
                        </Stack.Item>
                        <Stack.Item>
                            <UserInfoTable indexSymbol={selectedIndexOption as string} etfSymbol={selectedETFOption as string} ></UserInfoTable>
                        </Stack.Item>
                        <Stack.Item>
                            <TopDataBar indexSymbol={selectedIndexOption as string} etfSymbol={selectedETFOption as string} />
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
                                        title='Index期权'
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
                        <Stack horizontal styles={{ root: { height: '100%', width: '85%' } }} tokens={{ childrenGap: 20 }}>
                            <Stack tokens={{ childrenGap: 10 }} styles={{ root: { height: '100%', width: '50%' } }}>
                                <Stack styles={{ root: { height: '20%' } }}>
                                    <WingModelBar symbol={selectedIndexOption} />
                                </Stack>

                                <OptionGreeks symbol={selectedIndexOption} />
                            </Stack>
                            <Stack tokens={{ childrenGap: 10 }} styles={{ root: { height: '100%', width: '50%' } }}>
                                <Stack styles={{ root: { height: '20%' } }}>
                                    <WingModelBar symbol={selectedETFOption} />
                                </Stack>
                                <OptionGreeks symbol={selectedETFOption} />
                            </Stack>
                        </Stack>
                    </Stack>
                </Stack>
            </PivotItem>
            <PivotItem headerText='综合'>
                <Stack tokens={{ childrenGap: 20 }} styles={{ root: { height: '100vh', width: '100vw' } }}>
                    <Dropdown
                        label="选择希腊字母类型"
                        options={greekOptions}
                        selectedKey={selectedGreek}
                        onChange={(_, option) => setSelectedGreek(option?.key as string)}
                    />
                </Stack>
            </PivotItem>

        </Pivot >


    )
};

export default TradingDashboard;
