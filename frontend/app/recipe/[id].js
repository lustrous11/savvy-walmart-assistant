import React, { useState, useEffect } from 'react';
// import { View, StyleSheet, ScrollView, ActivityIndicator } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
// import { Card, Title, Paragraph, List } from 'react-native-paper';
// import { getRecipeDetails } from '../../services/api';
// At the top, add Alert to the imports from react-native
import { View, StyleSheet, ScrollView, ActivityIndicator, Alert } from 'react-native';
// Add Button to the imports from react-native-paper
import { Card, Title, Paragraph, List, Button } from 'react-native-paper';
// Add our new API function
import { getRecipeDetails, addMissingIngredientsToList } from '../../services/api';
// import { Alert } from 'react-native';


export default function RecipeDetailScreen() {
  const { id } = useLocalSearchParams(); // Gets the recipe ID from the URL
  const [recipe, setRecipe] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const userId = 1; // Hardcoded user ID
  

  useEffect(() => {
    const fetchDetails = async () => {
      if (id) {
        try {
          setIsLoading(true);
          const response = await getRecipeDetails(id);
          setRecipe(response.data);
        } catch (error) {
          console.error("Failed to fetch recipe details:", error);
        } finally {
          setIsLoading(false);
        }
      }
    };
    fetchDetails();
  }, [id]);

  const handleAddToCart = async () => {
    try {
      const response = await addMissingIngredientsToList(userId, id);
      const addedItems = response.data.added_items;
      Alert.alert(
        "Success!",
        `Added ${addedItems.length} missing item(s) to your shopping list.`
      );
    } catch (error) {
      console.error("Failed to add to list:", error);
      Alert.alert("Error", "Could not add items to your list.");
    }
  };

  if (isLoading) {
    return <ActivityIndicator size="large" style={{ flex: 1 }} />;
  }

  if (!recipe) {
    return <Paragraph>Recipe not found.</Paragraph>;
  }

  return (
    <ScrollView style={styles.container}>
      <Card>
        <Card.Cover source={{ uri: recipe.image }} />
        <Card.Content>
          <Title style={styles.title}>{recipe.title}</Title>
          <Paragraph>Ready in: {recipe.readyInMinutes} minutes</Paragraph>
          <Paragraph>Servings: {recipe.servings}</Paragraph>
        </Card.Content>
      </Card>

      <Button 
        mode="contained" 
        icon="cart-plus" 
        onPress={handleAddToCart} 
        style={styles.button}
      >
        Add Missing Ingredients to List
      </Button>
     

      <Card style={styles.card}>
        <Card.Content>
          <Title>Ingredients</Title>
          {recipe.extendedIngredients.map((ingredient) => (
            <List.Item
              key={ingredient.id}
              title={ingredient.original}
              left={() => <List.Icon icon="leaf" />}
            />
          ))}
        </Card.Content>
      </Card>
      
      <Card style={styles.card}>
        <Card.Content>
          <Title>Instructions</Title>
          {/* A simple way to display instructions without HTML parsing */}
          <Paragraph>{recipe.instructions.replace(/<[^>]*>?/gm, '')}</Paragraph>
        </Card.Content>
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  title: {
    marginTop: 10,
    fontSize: 24,
    fontWeight: 'bold',
  },
  card: {
    margin: 16,
  },

  button: {
    margin: 16,
    paddingVertical: 8,
  }

});