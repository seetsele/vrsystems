import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, TextInput, Alert, Image, ScrollView } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation, useRoute } from '@react-navigation/native';
import * as ImagePicker from 'expo-image-picker';
import { useApp } from '../context/AppContext';

export default function CaptureScreen() {
  const navigation = useNavigation<any>();
  const route = useRoute<any>();
  const { addToQueue, desktopConnected } = useApp();
  
  const captureType = route.params?.type || 'text';
  const [content, setContent] = useState('');
  const [title, setTitle] = useState('');
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [priority, setPriority] = useState<'normal' | 'urgent'>('normal');

  const pickImage = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'Please grant camera roll access to select images.');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 0.8,
    });

    if (!result.canceled) {
      setImageUri(result.assets[0].uri);
    }
  };

  const takePhoto = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'Please grant camera access to take photos.');
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      quality: 0.8,
    });

    if (!result.canceled) {
      setImageUri(result.assets[0].uri);
    }
  };

  const handleSubmit = () => {
    if (!content && !imageUri) {
      Alert.alert('Required', 'Please enter content or select an image.');
      return;
    }

    const itemTitle = title || 
      (captureType === 'url' ? content.substring(0, 50) : 
       captureType === 'image' ? 'Image capture' : 
       content.substring(0, 50));

    addToQueue({
      type: captureType === 'camera' ? 'image' : captureType === 'link' ? 'url' : 'text',
      title: itemTitle,
      content: imageUri || content,
    });

    Alert.alert(
      'Added to Queue',
      desktopConnected 
        ? 'Item sent to desktop for verification.' 
        : 'Item queued. Will sync when desktop connects.',
      [{ text: 'OK', onPress: () => navigation.goBack() }]
    );
  };

  const getTypeConfig = () => {
    switch (captureType) {
      case 'camera':
        return { icon: 'camera', color: '#06b6d4', title: 'Capture Image', placeholder: 'Add notes about this image...' };
      case 'text':
        return { icon: 'text', color: '#8b5cf6', title: 'Text Claim', placeholder: 'Enter the claim or statement to verify...' };
      case 'link':
        return { icon: 'link', color: '#ec4899', title: 'URL / Link', placeholder: 'Paste article URL or social media link...' };
      case 'share':
        return { icon: 'share-social', color: '#fbbf24', title: 'Shared Content', placeholder: 'Paste shared content...' };
      default:
        return { icon: 'document-text', color: '#06b6d4', title: 'Capture', placeholder: 'Enter content...' };
    }
  };

  const config = getTypeConfig();

  return (
    <View style={styles.container}>
      <LinearGradient colors={['#09090b', '#0f1419', '#09090b']} style={StyleSheet.absoluteFill} />
      
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <View style={[styles.headerIcon, { backgroundColor: config.color + '30' }]}>
            <Ionicons name={config.icon as any} size={28} color={config.color} />
          </View>
          <Text style={styles.headerTitle}>{config.title}</Text>
          <Text style={styles.headerSubtitle}>Send to desktop for verification</Text>
        </View>

        {/* Camera Options */}
        {(captureType === 'camera' || captureType === 'share') && (
          <View style={styles.cameraSection}>
            {imageUri ? (
              <View style={styles.imagePreview}>
                <Image source={{ uri: imageUri }} style={styles.previewImage} />
                <TouchableOpacity style={styles.removeImage} onPress={() => setImageUri(null)}>
                  <Ionicons name="close-circle" size={28} color="#ef4444" />
                </TouchableOpacity>
              </View>
            ) : (
              <View style={styles.cameraButtons}>
                <TouchableOpacity style={styles.cameraBtn} onPress={takePhoto}>
                  <Ionicons name="camera" size={32} color="#06b6d4" />
                  <Text style={styles.cameraBtnText}>Take Photo</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.cameraBtn} onPress={pickImage}>
                  <Ionicons name="images" size={32} color="#8b5cf6" />
                  <Text style={styles.cameraBtnText}>From Gallery</Text>
                </TouchableOpacity>
              </View>
            )}
          </View>
        )}

        {/* Title Input */}
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>Title (optional)</Text>
          <TextInput
            style={styles.input}
            value={title}
            onChangeText={setTitle}
            placeholder="Give this item a name..."
            placeholderTextColor="#52525b"
          />
        </View>

        {/* Content Input */}
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>
            {captureType === 'camera' ? 'Notes' : 'Content'}
          </Text>
          <TextInput
            style={[styles.input, styles.textarea]}
            value={content}
            onChangeText={setContent}
            placeholder={config.placeholder}
            placeholderTextColor="#52525b"
            multiline
            numberOfLines={6}
            textAlignVertical="top"
          />
        </View>

        {/* Priority Toggle */}
        <View style={styles.prioritySection}>
          <Text style={styles.inputLabel}>Priority</Text>
          <View style={styles.priorityOptions}>
            <TouchableOpacity 
              style={[styles.priorityBtn, priority === 'normal' && styles.priorityActive]}
              onPress={() => setPriority('normal')}
            >
              <Ionicons name="time-outline" size={18} color={priority === 'normal' ? '#06b6d4' : '#71717a'} />
              <Text style={[styles.priorityText, priority === 'normal' && styles.priorityTextActive]}>Normal</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={[styles.priorityBtn, priority === 'urgent' && styles.priorityUrgent]}
              onPress={() => setPriority('urgent')}
            >
              <Ionicons name="alert-circle" size={18} color={priority === 'urgent' ? '#ef4444' : '#71717a'} />
              <Text style={[styles.priorityText, priority === 'urgent' && styles.priorityTextUrgent]}>Urgent</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Connection Status */}
        <View style={[styles.connectionNote, desktopConnected ? styles.connectedNote : styles.disconnectedNote]}>
          <Ionicons 
            name={desktopConnected ? 'checkmark-circle' : 'cloud-offline-outline'} 
            size={18} 
            color={desktopConnected ? '#10b981' : '#71717a'} 
          />
          <Text style={styles.connectionText}>
            {desktopConnected 
              ? 'Desktop connected. Item will be sent immediately.' 
              : 'Desktop offline. Item will queue locally.'}
          </Text>
        </View>

        {/* Submit Button */}
        <TouchableOpacity style={styles.submitBtn} onPress={handleSubmit}>
          <LinearGradient colors={['#06b6d4', '#8b5cf6']} style={styles.submitGradient}>
            <Ionicons name="send" size={20} color="#fff" />
            <Text style={styles.submitText}>Send to Desktop</Text>
          </LinearGradient>
        </TouchableOpacity>

        <View style={{ height: 40 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#09090b' },
  content: { flex: 1, padding: 16 },
  
  header: { alignItems: 'center', marginBottom: 32, marginTop: 8 },
  headerIcon: {
    width: 64,
    height: 64,
    borderRadius: 32,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  headerTitle: { color: '#fafafa', fontSize: 22, fontWeight: '700' },
  headerSubtitle: { color: '#71717a', fontSize: 14, marginTop: 4 },

  cameraSection: { marginBottom: 24 },
  cameraButtons: { flexDirection: 'row', gap: 12 },
  cameraBtn: {
    flex: 1,
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  cameraBtnText: { color: '#a1a1aa', fontSize: 13, marginTop: 8 },
  
  imagePreview: { position: 'relative' },
  previewImage: {
    width: '100%',
    height: 200,
    borderRadius: 16,
    backgroundColor: '#18181b',
  },
  removeImage: {
    position: 'absolute',
    top: 8,
    right: 8,
  },

  inputGroup: { marginBottom: 20 },
  inputLabel: { color: '#a1a1aa', fontSize: 13, fontWeight: '500', marginBottom: 8 },
  input: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    padding: 16,
    color: '#fafafa',
    fontSize: 15,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  textarea: { height: 140 },

  prioritySection: { marginBottom: 24 },
  priorityOptions: { flexDirection: 'row', gap: 12 },
  priorityBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    padding: 14,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  priorityActive: {
    backgroundColor: 'rgba(6, 182, 212, 0.15)',
    borderColor: 'rgba(6, 182, 212, 0.3)',
  },
  priorityUrgent: {
    backgroundColor: 'rgba(239, 68, 68, 0.15)',
    borderColor: 'rgba(239, 68, 68, 0.3)',
  },
  priorityText: { color: '#71717a', fontSize: 14, fontWeight: '500' },
  priorityTextActive: { color: '#06b6d4' },
  priorityTextUrgent: { color: '#ef4444' },

  connectionNote: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    padding: 14,
    borderRadius: 10,
    marginBottom: 24,
  },
  connectedNote: { backgroundColor: 'rgba(16, 185, 129, 0.1)' },
  disconnectedNote: { backgroundColor: 'rgba(113, 113, 122, 0.1)' },
  connectionText: { color: '#a1a1aa', fontSize: 13, flex: 1 },

  submitBtn: { borderRadius: 14, overflow: 'hidden' },
  submitGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
    paddingVertical: 16,
  },
  submitText: { color: '#fff', fontSize: 16, fontWeight: '600' },
});
