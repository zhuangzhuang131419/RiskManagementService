import React, { useState } from 'react';
import { Callout, DefaultButton, TextField, Stack, Toggle } from '@fluentui/react';
import { useId } from '@fluentui/react-hooks';

const CustomizedModel = () => {
    const [isCalloutVisible, setIsCalloutVisible] = useState(false);
    const [isCustomized, setIsCustomized] = useState<boolean>(false)
    const toggleId = useId('callout-toggle');

    const toggleCallout = () => {
        setIsCalloutVisible(!isCalloutVisible);
        setIsCustomized(!isCustomized)
    };

    const closeCallout = () => setIsCalloutVisible(false);

    return (
        <div>
            <Toggle
                id={toggleId}
                onText="Enable"
                offText="Disable"
                onChange={toggleCallout}
                checked={isCustomized}
            />
            
            {isCalloutVisible && (
                <Callout
                    target={`#${toggleId}`}
                    onDismiss={closeCallout}
                    setInitialFocus
                    directionalHint={12} // Bottom-left alignment
                >
                    <Stack horizontalAlign="start" tokens={{ childrenGap: 10, padding: 10 }}>
                        <TextField label="品种" />
                        <TextField label="ATMVOL" />
                        <TextField label="K1" />
                        <TextField label="K2" />
                        <TextField label="b" />
                    </Stack>
                    <Stack horizontal tokens={{ childrenGap: 10, padding: 10 }}>
                        <DefaultButton text="确定" onClick={closeCallout} />
                        <DefaultButton text="清空" onClick={() => { /* Clear inputs logic */ }} />
                    </Stack>
                </Callout>
            )}
        </div>
    );
};

export default CustomizedModel;
