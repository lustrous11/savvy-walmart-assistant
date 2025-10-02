import React, { useState, useEffect } from 'react';
import { View, StyleSheet, FlatList, Alert } from 'react-native';
import { TextInput, Button, List, IconButton, Text } from 'react-native-paper';
import { getPantryItems, addPantryItem, deletePantryItem } from '../../services/api';

export default function PantryScreen() {
  const [items, setItems] = useState([]);
  const [newItemName, setNewItemName] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const userId = 1; // Hardcoded user ID

  const fetchItems = async () => {
    console.log("Frontend: Attempting to fetch pantry items...");
    try {
      const response = await getPantryItems(userId);
      console.log("Frontend: Received data from backend:", response.data);
      setItems(response.data);
    } catch (error) {
      // This will print the full network error to your Expo terminal
      console.error("Frontend: FAILED to fetch pantry items:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, []);

  const handleAddItem = async () => {
    if (newItemName.trim() === '') return;
    console.log(`Frontend: Attempting to add item: ${newItemName}`);
    try {
      await addPantryItem(userId, { item_name: newItemName, expiry_date: null });
      console.log("Frontend: Add item successful. Refreshing list...");
      setNewItemName('');
      fetchItems(); // Refresh the list
    } catch (error) {
      console.error("Frontend: FAILED to add item:", error);
    }
  };

  const handleDeleteItem = async (itemId) => {
    console.log(`Frontend: Attempting to delete item: ${itemId}`);
    try {
        await deletePantryItem(itemId);
        console.log("Frontend: Delete item successful. Refreshing list...");
        fetchItems(); // Refresh list
    } catch (error) {
        console.error("Frontend: FAILED to delete item:", error);
    }
  };


  return (
    <View style={styles.container}>
      <View style={styles.inputContainer}>
        <TextInput
          label="Add new pantry item"
          value={newItemName}
          onChangeText={setNewItemName}
          style={{ flex: 1 }}
        />
        <Button mode="contained" onPress={handleAddItem} style={{ marginLeft: 8 }}>
          Add
        </Button>
      </View>
      <FlatList
        data={items}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <List.Item
            title={item.item_name}
            right={() => <IconButton icon="delete-outline" onPress={() => handleDeleteItem(item.id)} />}
          />
        )}
        refreshing={isLoading}
        onRefresh={fetchItems}
        ListEmptyComponent={<Text style={styles.infoText}>Your pantry is empty.</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  inputContainer: {
    flexDirection: 'row',
    padding: 16,
    alignItems: 'center',
  },
  infoText: {
    textAlign: 'center',
    marginTop: 20,
    fontSize: 16,
    color: 'gray',
  },
});