export type User = {
  id: string;
  name: string;
}

export type TopBarData = {
  greekLetters: {
    delta: number;
    vega: number;
    theta: number;
  };
  indexOptionCount: number;  // 指数期权数量
  etfOptionCount: number;    // ETF期权数量
  futureCount: number;       // 期货数量
  cashCombined: number;      // 现金结合
}