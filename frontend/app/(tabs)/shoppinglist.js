import React, { useState } from 'react';
import { View, StyleSheet, FlatList, ScrollView } from 'react-native';
import { useFocusEffect } from 'expo-router';
import { List, Text, Button, Card, Appbar, Checkbox, Divider, Chip } from 'react-native-paper';
import { getShoppingList } from '../../services/api';

const SubstitutionCard = ({ sub }) => (
  <View style={styles.substitutionContainer}>
    <Divider style={styles.divider} />
    <Text style={styles.subText}>Save ${sub.savings} by switching to:</Text>
    <Chip icon="check-circle" style={styles.subChip}>
      {sub.name}
    </Chip>
  </View>
);

export default function ShoppingListScreen() {
  const [list, setList] = useState([]);
  const [checkedItems, setCheckedItems] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const userId = 1;

  const fetchList = async () => {
    try {
      setIsLoading(true);
      const response = await getShoppingList(userId);
      setList(response.data);
    } catch (error) {
      console.error("Failed to fetch shopping list:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCheckItem = (itemName) => {
    setCheckedItems(prev => ({
      ...prev,
      [itemName]: !prev[itemName],
    }));
  };
  
  // useFocusEffect will refetch the data every time the screen comes into view
  useFocusEffect(
    React.useCallback(() => {
      fetchList();
    }, [])
  );

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.Content title="My Shopping List" />
        {/* In a full app, this button would clear the list */}
        <Appbar.Action icon="delete-sweep-outline" onPress={() => setList([])} />
      </Appbar.Header>
      <FlatList
        data={list}
        keyExtractor={(item, index) => `${item.name}-${index}`}
        renderItem={({ item }) => (
          <Card style={styles.card}>
            <Checkbox.Item
              label={item.name}
              status={checkedItems[item.name] ? 'checked' : 'unchecked'}
              onPress={() => handleCheckItem(item.name)}
              labelStyle={checkedItems[item.name] ? styles.checkedItem : null}
            />
            {item.substitution && <SubstitutionCard sub={item.substitution} />}
          </Card>
        )}
        refreshing={isLoading}
        onRefresh={fetchList}
        ListEmptyComponent={<Text style={styles.infoText}>Your shopping list is empty. Add items from a recipe!</Text>}
        contentContainerStyle={{ paddingVertical: 8 }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f0f4f7' },
  infoText: { textAlign: 'center', marginTop: 30, fontSize: 16, color: 'gray' },
  card: { marginHorizontal: 16, marginVertical: 6, elevation: 2 },
  checkedItem: { textDecorationLine: 'line-through', color: 'gray' },
  substitutionContainer: { paddingHorizontal: 16, paddingBottom: 16 },
  divider: { marginVertical: 12 },
  subText: { marginBottom: 8, fontSize: 14, color: 'green', fontWeight: 'bold'},
  subChip: { alignSelf: 'flex-start' },
});