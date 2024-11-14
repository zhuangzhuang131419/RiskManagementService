import { CashGreeksResponse, GreeksResponse, WingModelData } from "../Model/OptionData";

export interface IOptionDataProvider {
  fetchIndexOptionSymbols(): Promise<string[]>;
  fetchETFOptionSymbols(): Promise<string[]>;
  fetchOptionGreeks(symbol: string): Promise<GreeksResponse>;
  fetchWingModelParaBySymbol(symbol: string): Promise<WingModelData[]>;
  fetchWingModelPara(): Promise<{ [key: string]: WingModelData }>
  postWingModelPara(para: { [key: string]: WingModelData }): Promise<void>
  fetchOptionGreeksSummary(symbol: string): Promise<CashGreeksResponse>
  fetchFutureGreeksSummary(symbol: string): Promise<CashGreeksResponse>
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

  fetchOptionGreeks = async (symbol: string): Promise<GreeksResponse> => {
    const response = await fetch(`/api/option/greeks?symbol=${symbol}`);
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

  fetchWingModelParaBySymbol = async (symbol: string): Promise<WingModelData[]> => {
    const response = await fetch(`/api/option/wing_model?symbol=${symbol}`);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    // 解析并打印 JSON 数据
    const data = await response.json();
    // console.log('fetchWingModelParaBySymbol: ', data);

    return data;
  }

  fetchWingModelPara = async (): Promise<{ [key: string]: WingModelData }> => {
    const response = await fetch(`/api/option/wing_models`);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    // 解析并打印 JSON 数据
    const data: { [key: string]: WingModelData } = await response.json();
    // console.log('fetchWingModelPara: ', data);
    return data;
  }

  postWingModelPara = async (para: { [key: string]: WingModelData; }): Promise<void> => {
    const response = await fetch('/api/option/wing_models', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(para),
    });

    if (!response.ok) {
      throw new Error('Failed to update data');
    }
  }

  fetchOptionGreeksSummary = async (symbol: string): Promise<CashGreeksResponse> => {
    const response = await fetch(`/api/option/greeks_summary?symbol=${symbol}`);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    // 解析并打印 JSON 数据
    const data = await response.json();
    // console.log('fetchWingModelParaBySymbol: ', data);

    return data;
  }

  fetchFutureGreeksSummary = async (symbol: string): Promise<CashGreeksResponse> => {
    const response = await fetch(`/api/future/greeks_summary?symbol=${symbol}`);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    // 解析并打印 JSON 数据
    const data = await response.json();
    // console.log('fetchWingModelParaBySymbol: ', data);

    return data;
  }
}

export const optionDataProvider = new OptionDataProvider()