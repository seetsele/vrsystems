import React from 'react';
import { View, Modal, TextInput, StyleSheet, Text, TouchableOpacity } from 'react-native';

export default function VerifyOverlay({ visible, onClose, onVerify }: { visible: boolean; onClose: () => void; onVerify: (text: string) => void }) {
  const [text, setText] = React.useState('');

  return (
    <Modal visible={visible} transparent animationType="fade">
      <View style={styles.backdrop}>
        <View style={styles.card}>
          <Text style={styles.title}>Quick Verify</Text>
          <TextInput
            placeholder="Paste or type text to verify..."
            placeholderTextColor="#9CA3AF"
            style={styles.input}
            multiline
            value={text}
            onChangeText={setText}
          />
          <View style={styles.actions}>
            <TouchableOpacity style={styles.btnClose} onPress={() => { setText(''); onClose(); }}>
              <Text style={styles.btnCloseText}>Close</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.btnVerify} onPress={() => { if (text.trim()) { onVerify(text.trim()); setText(''); onClose(); } }}>
              <Text style={styles.btnVerifyText}>Verify</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: { flex: 1, backgroundColor: 'rgba(0,0,0,0.6)', alignItems: 'center', justifyContent: 'center' },
  card: { width: '90%', backgroundColor: '#0b0b0c', padding: 16, borderRadius: 12, borderWidth: 1, borderColor: 'rgba(255,255,255,0.04)' },
  title: { color: '#fff', fontSize: 16, marginBottom: 8 },
  input: { minHeight: 80, maxHeight: 200, color: '#fff', backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: 8, padding: 10, textAlignVertical: 'top' },
  actions: { flexDirection: 'row', justifyContent: 'flex-end', gap: 8, marginTop: 12 },
  btnClose: { paddingVertical: 8, paddingHorizontal: 12 },
  btnCloseText: { color: '#9CA3AF' },
  btnVerify: { paddingVertical: 8, paddingHorizontal: 14, backgroundColor: '#f59e0b', borderRadius: 8 },
  btnVerifyText: { color: '#000', fontWeight: '700' }
});
