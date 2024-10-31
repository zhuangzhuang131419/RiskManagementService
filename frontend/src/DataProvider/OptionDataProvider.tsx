import { GreeksResponse, WingModelData } from "../Model/OptionData";

export interface IOptionDataProvider {
  fetchIndexOptionSymbols(): Promise<string[]>;
  fetchETFOptionSymbols(): Promise<string[]>;
  fetchOptionGreeks(symbol: string, exchange: string): Promise<GreeksResponse>;
  fetchWingModelParaBySymbol(symbol: string, exchange: string): Promise<WingModelData>;
  fetchWingModelPara(): Promise<{ [key: string]: WingModelData }>
}

class OptionDataProvider implements IOptionDataProvider {
  fetchIndexOptionSymbols = async (): Promise<string[]> => {
    const response = await fetch('/api/cffex/options');
    if (!response.ok) {
      throw new Error('Failed to fetch options');
    }
    return response.json();
    // return ["IO2410", "IO2411", "IO2412", "HO2410", "HO2411", "HO2412"];
  };

  fetchETFOptionSymbols = async (): Promise<string[]> => {
    const response = await fetch('/api/se/options');
    if (!response.ok) {
      throw new Error('Failed to fetch options');
    }
    return response.json();
    // return ["IO2410", "IO2411", "IO2412", "HO2410", "HO2411", "HO2412"];
  };

  fetchOptionGreeks = async (symbol: string, exchange: string): Promise<GreeksResponse> => {
    const response = await fetch(`/api/${exchange}/option/greeks?symbol=${symbol}`);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    console.log('symbol' + symbol)
    // 打印响应状态
    console.log('Response status: ' + response.status);
    console.log('Response status text: ' + response.statusText);

    // 解析并打印 JSON 数据
    const data = await response.json();
    console.log('fetchOptionGreeks: ', data);

    return data;
    // return mockGreeksResponse;
  };

  fetchWingModelParaBySymbol = async (symbol: string, exchange: string): Promise<WingModelData> => {
    const response = await fetch(`/api/${exchange}/option/wing_model?symbol=${symbol}`);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    // 解析并打印 JSON 数据
    const data = await response.json();
    // console.log('fetchWingModelParaBySymbol: ', data);

    return data;
  }

  fetchWingModelPara = async (): Promise<{ [key: string]: WingModelData }> => {
    const response = await fetch(`/api/option/wing_model`);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    // 解析并打印 JSON 数据
    const data: { [key: string]: WingModelData } = await response.json();
    console.log('fetchWingModelPara: ', data);
    return data;
  }
}

export const mockGreeksResponse: GreeksResponse = {
  symbol: 'IO2410',
  strike_prices: {
    '4000': {
      call_option: {
        delta: 0.65,
        gamma: 0.12,
        vega: 0.25,
        theta: -0.10,
        vanna_sv: 0.1,
        vanna_vs: 0.1
      },
      put_option: {
        delta: -0.35,
        gamma: 0.10,
        vega: 0.20,
        theta: -0.08,
        vanna_sv: 0.1,
        vanna_vs: 0.1
      },
    },
    '4100': {
      call_option: {
        delta: 0.55,
        gamma: 0.11,
        vega: 0.22,
        theta: -0.09,
        vanna_sv: 0.1,
        vanna_vs: 0.1
      },
      put_option: {
        delta: -0.45,
        gamma: 0.09,
        vega: 0.19,
        theta: -0.07,
        vanna_sv: 0.1,
        vanna_vs: 0.1
      },
    },
    '4200': {
      call_option: {
        delta: 0.45,
        gamma: 0.10,
        vega: 0.21,
        theta: -0.08,
        vanna_sv: 0.1,
        vanna_vs: 0.1
      },
      put_option: {
        delta: -0.55,
        gamma: 0.08,
        vega: 0.18,
        theta: -0.06,
        vanna_sv: 0.1,
        vanna_vs: 0.1
      },
    },
  },
};


export const optionDataProvider = new OptionDataProvider()