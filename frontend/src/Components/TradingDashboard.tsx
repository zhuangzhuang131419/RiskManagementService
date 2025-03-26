import React, { useEffect, useState } from 'react';
import { Stack, Text, Pivot, PivotItem, IDropdownOption, Dropdown, DetailsList, DetailsListLayoutMode, SelectionMode } from '@fluentui/react';
import OptionGreeks from './OptionGreeks';
import { useQuery } from 'react-query';
import UserSelector from './UserSelector';
import ScrollBox from './ScrollBox';
import { optionDataProvider } from '../DataProvider/OptionDataProvider';
import TopDataBar from './TopDataBar';
import { User, UserGreeks } from '../Model/User';
import { userDataProvider } from '../DataProvider/UserDataProvider';
import WingModelBar from './WingModelBar';
import BaselineSelector from './BaselineSelector';
import UserInfoTable from './UserInfoTable';
import TheoreticalLineAuxiliaryChart from './TheoreticalLineAuxiliaryChart';

document.body.style.overflow = 'hidden';
document.documentElement.style.overflow = 'hidden';
document.title = "风控"

const TradingDashboard: React.FC = () => {

    const [selectedIndexOption, setSelectedIndexOption] = useState<string | null>(null);
    const [selectedETFOption, setSelectedETF] = useState<string | null>(null);
    const [selectedBaseline, setSelectedBaseline] = useState<string>();
    const [clock, setClock] = useState<string>();

    useQuery<string>(
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

    const { data: userItems = [] } = useQuery<User[]>(
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

    useQuery(
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


    const { data: greeksTotalItems = [] } = useQuery(
        ['greeksTotal'],
        userDataProvider.fetchGreeksTotal,
        {
            onSuccess(data) {
                console.log('fetchGreeksTotal:' + JSON.stringify(data))

            },
            refetchOnWindowFocus: false,
            refetchInterval: 1000 * 3,
        }

    );

    const [selectedGreek, setSelectedGreek] = useState<string>('delta_cash');

    const [greeksItem, setGreeksItem] = useState<UserGreeks[]>([])

    useEffect(() => {
        if (greeksTotalItems.length > 0) {
            const transformedItems = greeksTotalItems.map((item) => ({
                user: item.user,
                SSE50: item.SSE50?.[selectedGreek] ?? 0, // Get value for selectedGreek or default to 0
                CSI300: item.CSI300?.[selectedGreek] ?? 0,
                CSI500: item.CSI500?.[selectedGreek] ?? 0,
                CSI1000: item.CSI1000?.[selectedGreek] ?? 0,
            }));
            console.log(JSON.stringify(transformedItems))
            setGreeksItem(transformedItems);
        }
    }, [selectedGreek, greeksTotalItems]);

    // 希腊字母下拉框选项
    const greekOptions: IDropdownOption[] = [
        { key: 'delta_cash', text: 'Cash Delta' },
        { key: 'vega_cash', text: 'Cash Vega' },
        { key: 'theta_cash', text: 'Cash Theta' },
        { key: 'gamma_p_cash', text: 'Cash GammaP' },
        { key: 'db_cash', text: 'Cash DB' },
        { key: 'vanna_vs_cash', text: 'Cash VannaVS' },
        { key: 'vanna_sv_cash', text: 'Cash VannaSV' },
        { key: 'dkurt_cash', text: 'Cash DKurt' },
    ];

    const greekColumns = [
        {
            key: 'column0',
            name: '账户品种',
            fieldName: 'user',
            minWidth: 150,
        },
        {
            key: 'column1',
            name: '50汇总',
            fieldName: 'SSE50',
            minWidth: 150,
            onRender: (item: UserGreeks) => formatPercentage(item.SSE50),
        },
        {
            key: 'column2',
            name: '300汇总',
            fieldName: 'CSI300',
            minWidth: 150,
            onRender: (item: UserGreeks) => formatPercentage(item.CSI300),
        },
        {
            key: 'column3',
            name: '500汇总',
            fieldName: 'CSI500',
            minWidth: 150,
            onRender: (item: UserGreeks) => formatPercentage(item.CSI500),
        },
        {
            key: 'column4',
            name: '1000汇总',
            fieldName: 'CSI1000',
            minWidth: 150,
            onRender: (item: UserGreeks) => formatPercentage(item.CSI1000),
        },
    ];

    const { data: monitorTotalItems = [] } = useQuery(
        ['monitorTotal'],
        userDataProvider.fetchMonitorIndexTotal,
        {
            onSuccess(data) {
                console.log('fetchMonitorIndexTotal:' + JSON.stringify(data))

            },
            refetchOnWindowFocus: false,
            refetchInterval: 1000 * 3,
        }

    );

    const monitorColumns = [
        { key: 'account', name: '账户品种', fieldName: 'user', minWidth: 150 },
        { key: '50_summary', name: '50汇总', fieldName: 'SSE50', minWidth: 150 },
        { key: '300_summary', name: '300汇总', fieldName: 'CSI300', minWidth: 150 },
        { key: '500_summary', name: '500汇总', fieldName: 'CSI500', minWidth: 150 },
    ];

    const formatPercentage = (value: number | null): string =>
        value !== null && !isNaN(value) ? `${(value).toFixed(2)}` : '--';

    return (
        <Pivot>
            <PivotItem headerText='风险值'>
                <TheoreticalLineAuxiliaryChart></TheoreticalLineAuxiliaryChart>
            </PivotItem>
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
                    <Stack horizontal tokens={{ childrenGap: 20 }} >
                        <Stack tokens={{ childrenGap: 20 }} styles={{ root: { height: '100%', width: '50%' } }}>
                            <DetailsList
                                items={greeksItem}
                                columns={greekColumns}
                                layoutMode={DetailsListLayoutMode.justified}
                                selectionMode={SelectionMode.none}
                                selectionPreservedOnEmptyClick={true}
                                compact={true}
                            />
                            <Dropdown
                                label="选择希腊字母类型"
                                options={greekOptions}
                                selectedKey={selectedGreek}
                                onChange={(_, option) => setSelectedGreek(option?.key as string)}
                            />
                        </Stack>
                        <Stack tokens={{ childrenGap: 20 }} styles={{ root: { height: '100%', width: '50%' } }}>
                            <DetailsList
                                items={monitorTotalItems}
                                columns={monitorColumns}
                                layoutMode={DetailsListLayoutMode.justified}
                                selectionMode={SelectionMode.none}
                                selectionPreservedOnEmptyClick={true}
                                compact={true}
                            />
                        </Stack>
                    </Stack>
                </Stack>
            </PivotItem>
        </Pivot >
    )
};

export default TradingDashboard;
