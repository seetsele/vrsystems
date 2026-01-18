import React from 'react';
import { TouchableOpacity, View, Text, StyleSheet } from 'react-native';

export default function VerifyFAB({ onPress }: { onPress: () => void }) {
  return (
    <View style={styles.container} pointerEvents="box-none">
      <TouchableOpacity style={styles.fab} onPress={onPress}>
        <Text style={styles.icon}>V</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { position: 'absolute', bottom: 90, right: 20, zIndex: 9999 },
  fab: { width: 56, height: 56, borderRadius: 28, backgroundColor: '#f59e0b', alignItems: 'center', justifyContent: 'center', elevation: 6 },
  icon: { fontWeight: '700', color: '#000' }
});
