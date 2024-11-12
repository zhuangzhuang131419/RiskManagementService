import React, { useEffect, useState } from 'react';
import { ChoiceGroup, Stack, IChoiceGroupOption, Dialog } from '@fluentui/react';
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
    const [selectedIndexOption, setSelectedIndexOption] = useState<string>("");
    const [selectedFuture, setSelectedFuture] = useState<string | null>(null);
    const [selectedETFOption, setSelectedETF] = useState<string>("");
    const [selectedBaseline, setSelectedBaseline] = useState<string>();

    const { data: userItems, isFetching: isUserFetching } = useQuery(
        ['users'],
        userDataProvider.fetchUsers,
    );

    const { data: indexOptionItems, isFetching: isIndexOptionFetching } = useQuery(
        ['indexOptions'],
        optionDataProvider.fetchIndexOptionSymbols,
        {
            select(data) {
                return data.map((item) => ({ key: item }))
            },
            onSuccess(data) {
                console.log('selected: ' + selectedIndexOption)
                console.log('fetch user data' + JSON.stringify(indexOptionItems))
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
        }
    );

    useEffect(() => {
        console.log('TradingDashboard' + selectedIndexOption)
    }, [selectedIndexOption])

    return (

        // 主布局
        <Stack tokens={{ childrenGap: 20 }} styles={{ root: { height: '100vh', width: '100%' } }}>
            {/* 顶部：账户选择器和数据展示 */}
            <Stack horizontal tokens={{ childrenGap: 20 }}>
                <Stack.Item>
                    {!isUserFetching && (
                        <UserSelector accounts={userItems as User[]} onSelect={setSelectedUserKey} selectedUserKey={selectedUserKey} />
                    )}
                </Stack.Item>
                <Stack.Item>
                    <UserInfoTable></UserInfoTable>
                </Stack.Item>
                <Stack.Item>
                    <TopDataBar indexSymbol={selectedIndexOption as string} etfSymbol={selectedETFOption as string} />
                </Stack.Item>
            </Stack>



            {/* 中间部分：期权滚动框和期权希腊字母展示 */}
            <Stack horizontal tokens={{ childrenGap: 20 }} styles={{ root: { height: '90%' } }}>
                {/* 左侧：ScrollBox */}
                <Stack tokens={{ childrenGap: 10 }} styles={{ root: { width: '15%' } }}>
                    {!isIndexOptionFetching && (
                        <Stack styles={{ root: { height: '35%' } }}>
                            <ScrollBox
                                items={indexOptionItems as { key: string }[]}
                                onClick={setSelectedIndexOption}
                                renderItem={(item) => item.key}
                                title='指数期权'
                                selectedItemKey={selectedIndexOption}
                            />
                        </Stack>
                    )}
                    {/* {!isFutureFetching && (
                        <Stack styles={{ root: { height: '30%' } }}>
                            <ScrollBox
                                items={futureItems as string[]}
                                onClick={setSelectedFuture}
                                renderItem={(item) => item as string}
                                title='期货'
                            />
                        </Stack> 
                    )} */}
                    {!isETFOptionFetching && (
                        <Stack styles={{ root: { height: '35%', overflowY: 'auto' } }}>
                            <ScrollBox
                                items={etfOptionItems as { key: string }[]}
                                onClick={setSelectedETF}
                                renderItem={(item) => item.key}
                                title='ETF期权'
                                selectedItemKey={selectedETFOption}
                            />
                        </Stack>
                    )}
                    <Stack styles={{ root: { height: '20%' } }}>
                        <BaselineSelector
                            onSelect={setSelectedBaseline}
                            selectedBaselineKey={selectedBaseline as string}
                        />
                    </Stack>
                    <Stack styles={{ root: { height: '10%' } }}>
                        <CustomizedParaDialog></CustomizedParaDialog>
                    </Stack>
                </Stack>

                {/* 右侧：OptionGreeks */}
                {/* <Stack horizontal tokens={{ childrenGap: 10 }} grow={1} styles={{ root: { height: '100%' } }}>
                        <Stack tokens={{ childrenGap: 10 }} styles={{ root: { flex: 1 } }}>
                            <WingModelBar symbol={selectedIndexOption} style={{ flex: '0 0 10%' }} />
                            <OptionGreeks symbol={selectedIndexOption} style={{ flex: '1 1 auto', overflowY: 'auto', height: '90%' }} />
                        </Stack>
                        <Stack tokens={{ childrenGap: 10 }} styles={{ root: { flex: 1 } }}>
                            <WingModelBar symbol={selectedETFOption} style={{ flex: '0 0 10%' }} />
                            <OptionGreeks symbol={selectedETFOption} style={{ flex: '1 1 auto', overflowY: 'auto', height: '90%' }} />
                        </Stack>
                    </Stack> */}
            </Stack>
        </Stack>
    )
};

export default TradingDashboard;
