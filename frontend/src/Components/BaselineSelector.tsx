import { Dropdown } from "@fluentui/react";
import { useQuery } from "react-query";
import { userDataProvider } from "../DataProvider/UserDataProvider";
import { useState } from "react";



// 定义组件的 props 类型
interface BaselineSelectorProps {
  onSelect: (accountId: string) => void; // onSelect 函数接受选中的账户 ID
  selectedBaselineKey: string;
}

const BaselineSelector: React.FC<BaselineSelectorProps> = ({ onSelect, selectedBaselineKey }) => {
  const options = [
    { key: 'average', text: '平均基准' },
    { key: 'sh', text: '上交基准' },
    { key: 'individual', text: '各自基准' },
  ];

  // 保存当前选中的基准类型
  const [selectedBaseline, setSelectedBaseline] = useState<string>(selectedBaselineKey);

  const { data, isFetching } = useQuery(
    ['baseline'],
    userDataProvider.fetchBaseline,
    {
      select(data) {
        return data
      },
      onSuccess(data) {
        setSelectedBaseline(data);
      },
    }
  );

  const onBaselineChange = async (baseline: string) => {
    onSelect(baseline);
    setSelectedBaseline(baseline)

    try {
      userDataProvider.setBaseline(baseline)
    } catch (error) {
      console.log("postBaseline:" + error)
    }
  }

  if (isFetching) {
    return <p>获取数据中...</p>
  }

  return (
    <Dropdown
      placeholder="选择基准"
      label="基准选择"
      options={options}
      selectedKey={selectedBaseline}
      onChange={(event, option) => onBaselineChange(option?.key as string)}
    />
  );
};

export default BaselineSelector;