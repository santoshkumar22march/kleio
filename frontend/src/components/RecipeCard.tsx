/**
 * Recipe Card Component
 * Display recipe summary with available ingredients
 */

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Clock, ChefHat, Users, Check, X } from 'lucide-react';

interface RecipeIngredient {
  item: string;
  quantity: number;
  unit: string;
  available: boolean;
  note?: string;
}

interface Recipe {
  recipe_name: string;
  description: string;
  cooking_time_minutes: number;
  difficulty: string;
  cuisine: string;
  servings: number;
  ingredients: RecipeIngredient[];
  instructions: string[];
  tips: string[];
  nutrition: {
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
    fiber: number;
  };
}

interface RecipeCardProps {
  recipe: Recipe;
  onViewDetails: () => void;
  compact?: boolean;
}

const RecipeCard = ({ recipe, onViewDetails, compact = false }: RecipeCardProps) => {
  const availableCount = recipe.ingredients.filter(i => i.available).length;
  const totalCount = recipe.ingredients.length;
  const availabilityPercentage = Math.round((availableCount / totalCount) * 100);

  const getDifficultyColor = (difficulty: string) => {
    const colors: Record<string, string> = {
      'easy': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100',
      'medium': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100',
      'hard': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100',
    };
    return colors[difficulty.toLowerCase()] || 'bg-gray-100 text-gray-800';
  };

  return (
    <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={onViewDetails}>
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1">
            <CardTitle className="text-lg sm:text-xl">{recipe.recipe_name}</CardTitle>
            <CardDescription className="mt-1">{recipe.description}</CardDescription>
          </div>
          <Badge className={getDifficultyColor(recipe.difficulty)} variant="secondary">
            {recipe.difficulty}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Recipe Meta */}
        <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <Clock className="w-4 h-4" />
            <span>{recipe.cooking_time_minutes} mins</span>
          </div>
          <div className="flex items-center gap-1">
            <Users className="w-4 h-4" />
            <span>{recipe.servings} servings</span>
          </div>
          <div className="flex items-center gap-1">
            <ChefHat className="w-4 h-4" />
            <span>{recipe.cuisine}</span>
          </div>
        </div>

        {/* Ingredient Availability */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium">Ingredients</span>
            <span className={`${availabilityPercentage >= 80 ? 'text-green-600' : availabilityPercentage >= 50 ? 'text-yellow-600' : 'text-orange-600'} font-medium`}>
              {availableCount}/{totalCount} available
            </span>
          </div>
          
          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700">
            <div 
              className={`h-2 rounded-full ${availabilityPercentage >= 80 ? 'bg-green-600' : availabilityPercentage >= 50 ? 'bg-yellow-600' : 'bg-orange-600'}`}
              style={{ width: `${availabilityPercentage}%` }}
            />
          </div>

          {/* Ingredient Preview (compact) */}
          {!compact && (
            <div className="flex flex-wrap gap-2 mt-3">
              {recipe.ingredients.slice(0, 6).map((ingredient, idx) => (
                <Badge 
                  key={idx} 
                  variant={ingredient.available ? "default" : "outline"}
                  className="text-xs"
                >
                  {ingredient.available ? (
                    <Check className="w-3 h-3 mr-1" />
                  ) : (
                    <X className="w-3 h-3 mr-1" />
                  )}
                  {ingredient.item}
                </Badge>
              ))}
              {recipe.ingredients.length > 6 && (
                <Badge variant="secondary" className="text-xs">
                  +{recipe.ingredients.length - 6} more
                </Badge>
              )}
            </div>
          )}
        </div>

        {/* Nutrition */}
        {!compact && (
          <div className="flex gap-4 text-xs text-muted-foreground border-t pt-3">
            <span>🔥 {recipe.nutrition.calories} cal</span>
            <span>💪 {recipe.nutrition.protein}g protein</span>
            <span>🌾 {recipe.nutrition.carbs}g carbs</span>
          </div>
        )}

        {/* View Button */}
        <Button className="w-full" variant="outline" onClick={onViewDetails}>
          View Recipe
        </Button>
      </CardContent>
    </Card>
  );
};

export default RecipeCard;
