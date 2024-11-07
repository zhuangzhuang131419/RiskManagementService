import React from 'react';
import TradingDashboard from './Components/TradingDashboard';
import { QueryClient, QueryClientProvider } from 'react-query';
import { initializeIcons } from '@fluentui/react';
import { createTheme, ThemeProvider } from '@fluentui/react';

const queryClient = new QueryClient();
initializeIcons();


const darkTheme = createTheme({
  palette: {
    themePrimary: '#ffffff',
    themeLighterAlt: '#f8f8f8',
    themeLighter: '#e1e1e1',
    themeLight: '#c8c8c8',
    themeTertiary: '#a3a3a3',
    themeSecondary: '#8a8a8a',
    themeDarkAlt: '#595959',
    themeDark: '#3d3d3d',
    themeDarker: '#2c2c2c',
    neutralLighterAlt: '#3c3c3c',
    neutralLighter: '#383838',
    neutralLight: '#333333',
    neutralQuaternaryAlt: '#2e2e2e',
    neutralQuaternary: '#2b2b2b',
    neutralTertiaryAlt: '#2a2a2a',
    neutralTertiary: '#d0d0d0',
    neutralSecondary: '#e0e0e0',
    neutralPrimaryAlt: '#eaeaea',
    neutralPrimary: '#ffffff',
    neutralDark: '#f4f4f4',
    black: '#f8f8f8',
    white: '#000000',
  },
});


const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={darkTheme}>
        <TradingDashboard></TradingDashboard>
      </ThemeProvider>
    </QueryClientProvider>

  );
};

export default App;
