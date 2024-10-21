import React, { useState } from 'react';
import { Stack } from '@fluentui/react';
import OptionList from './components/OptionList';
import OptionGreeks from './components/OptionGreeks';
import { initializeIcons } from '@fluentui/react';
import { QueryClient, QueryClientProvider } from 'react-query';

const stackStyles = {
    root: {
        width: '100%',
        marginTop: '20px',
    },
};

const columnProps = {
    tokens: { childrenGap: 15 },
    styles: { root: { width: '10%' } },
};

const queryClient = new QueryClient();
initializeIcons();

const App: React.FC = () => {
    const [selectedOption, setSelectedOption] = useState<string | null>(null);

    return (
      <QueryClientProvider client={queryClient}>
        <Stack horizontal tokens={{ childrenGap: 50 }} styles={stackStyles}>
            {/* 左侧的 OptionList */}
            <Stack {...columnProps}>
                <OptionList onSelect={setSelectedOption} />
            </Stack>

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
                    <p>Please select an option to view its Greeks data. {selectedOption}</p>
                )}
            </Stack>
        </Stack>
      </QueryClientProvider>
        
    );
};

export default App;
