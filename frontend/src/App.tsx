import React, { useState } from 'react';
import TradingDashboard from './Components/TradingDashboard';
import { QueryClient, QueryClientProvider, useQuery } from 'react-query';
import { initializeIcons } from '@fluentui/react';

const queryClient = new QueryClient();
initializeIcons();

const App: React.FC = () => {

    return (
      <QueryClientProvider client={queryClient}>
        <TradingDashboard></TradingDashboard>
      </QueryClientProvider>
        
    );
};

export default App;
