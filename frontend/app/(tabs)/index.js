import React, { useState } from 'react';
import { View, StyleSheet, FlatList, ActivityIndicator, Text } from 'react-native';
import { TextInput, Button, Card, Title, Paragraph } from 'react-native-paper';
import { getRecommendations } from '../../services/api';
import { Link } from 'expo-router';

const RecipeCard = ({ item }) => (
    <Card style={styles.card}>
      <Card.Cover source={{ uri: item.image }} />
      <Card.Content>
        <Title>{item.title}</Title>
      </Card.Content>
    </Card>
);

export default function PlannerScreen() {
  const [query, setQuery] = useState('');
  const [recipes, setRecipes] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searched, setSearched] = useState(false); // To track if a search has been performed

  const RecipeCard = ({ item }) => (
  <Link href={`/recipe/${item.id}`} asChild>
    <Card style={styles.card}>
      <Card.Cover source={{ uri: item.image }} />
      <Card.Content>
        <Title>{item.title}</Title>
      </Card.Content>
    </Card>
  </Link>
);


  const handleSearch = async () => {
    if (!query.trim()) return;
    setIsLoading(true);
    setSearched(true);
    try {
      const response = await getRecommendations(1, query);
      setRecipes(response.data.recipes);
    } catch (error) {
      console.error("Failed to fetch recommendations:", error);
      setRecipes([]); // Clear recipes on error
    } finally {
      setIsLoading(false);
    }
  };

  const renderContent = () => {
    if (isLoading) {
      return <ActivityIndicator size="large" style={{ marginTop: 20 }} />;
    }
    if (searched && recipes.length === 0) {
      return <Text style={styles.infoText}>No recipes found. Try a different search!</Text>;
    }
    return (
        <FlatList
            data={recipes}
            keyExtractor={(item) => item.id.toString()}
            renderItem={({ item }) => <RecipeCard item={item} />}
            contentContainerStyle={{ paddingVertical: 10 }}
        />
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.inputContainer}>
        <TextInput
            label="e.g., healthy chicken dinner under 30 mins"
            value={query}
            onChangeText={setQuery}
            style={styles.input}
        />
        <Button mode="contained" onPress={handleSearch} loading={isLoading} disabled={isLoading}>
            Find Meals
        </Button>
      </View>
      {renderContent()}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  inputContainer: {
    padding: 16,
    backgroundColor: 'white',
  },
  input: {
    marginBottom: 16,
  },
  card: {
    marginHorizontal: 16,
    marginVertical: 8,
  },
  infoText: {
    textAlign: 'center',
    marginTop: 20,
    fontSize: 16,
    color: 'gray',
  },
});