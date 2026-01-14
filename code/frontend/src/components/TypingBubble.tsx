import React, { useEffect, useRef } from "react";
import { Animated, View } from "react-native";

export function TypingBubble({ styles }: {styles: any}) {
    const a = useRef(new Animated.Value(0.3)).current;
    const b = useRef(new Animated.Value(0.3)).current;
    const c = useRef(new Animated.Value(0.3)).current;

    useEffect(() => {
        const pulse = (v: Animated.Value, delay: number) =>
          Animated.loop(
            Animated.sequence([
              Animated.delay(delay),
              Animated.timing(v, { toValue: 1, duration: 300, useNativeDriver: true }),
              Animated.timing(v, { toValue: 0.3, duration: 300, useNativeDriver: true }),
              Animated.delay(150),
            ])
          );
        const p1 = pulse(a, 0);
        const p2 = pulse(b, 150);
        const p3 = pulse(c, 300);

        p1.start(); p2.start(); p3.start();
        return () => { p1.stop(); p2.stop(); p3.stop(); };
    }, [a, b, c]);

    return (
        <View style={[styles.bubble, styles.assistantBubble, styles.TypingBubble]}>
            <View style={styles.dotsRow}>
                <Animated.View style={[styles.dot, { opacity: a}]} />
                <Animated.View style={[styles.dot, { opacity: b}]} />
                <Animated.View style={[styles.dot, { opacity: c}]} />
            </View>
        </View>
    )
}