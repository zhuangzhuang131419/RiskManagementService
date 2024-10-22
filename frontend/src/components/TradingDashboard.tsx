import React, { useState } from 'react';
import { Stack } from '@fluentui/react';
import OptionGreeks from './OptionGreeks';
import { QueryClient, QueryClientProvider, useQuery } from 'react-query';
import AccountSelector from './AccountSelector';
import ScrollBox from './ScrollBox';
import { symbolName } from 'typescript';
import { optionDataProvider } from '../DataProvider/OptionDataProvider';

const stackStyles = {
    root: {
        width: '100%',
        marginTop: '20px',
    },
};




const TradingDashboard: React.FC = () => {
    const [selectedAccount, setSelectedAccount] = useState<string>("account1");
    const [selectedOption, setSelectedOption] = useState<string | null>(null);
    const [selectedFuture, setSelectedFuture] = useState(null);

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

    const { data: optionItems, error, isFetching: isOptionFetching } = useQuery(
        ['options'],
        optionDataProvider.fetchOptionSymbols,
    );

    return (
        <Stack>
            <Stack.Item>
                <AccountSelector accounts={accounts} onSelect={setSelectedAccount} />
                {!isOptionFetching && <ScrollBox items={optionItems} onClick={setSelectedOption} renderItem={(item) => item as string} />}
            </Stack.Item>
            <Stack horizontal tokens={{ childrenGap: 50 }} styles={stackStyles}>
            {/* 左侧的 OptionList */}
            {/* <Stack {...columnProps}>
                <OptionList onSelect={setSelectedOption} />
            </Stack> */}

            {/* 右侧的 OptionGreeks */}
            <Stack
                styles={{
                    root: {
                        width: '40%'
                    }
                }}>
                {selectedOption ? (
                    <OptionGreeks symbol={selectedOption} />
                ) : (
                    <p>请选择一个期权以查看其希腊字母数据。{selectedOption}</p>
                )}
                </Stack>
            </Stack>
        </Stack>
    )
};

export default TradingDashboard;
