import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import api from '@/lib/api';
import {
  TrendingUp,
  Calendar,
  Package,
  Activity,
  Search,
  AlertCircle,
  ChevronRight,
  BarChart3
} from 'lucide-react';

interface PatternData {
  purchase_frequency_days: number | null;
  avg_quantity_purchased: number | null;
  consumption_rate_per_day: number | null;
  data_points: number;
}

interface PredictionData {
  depletion_date: string | null;
  suggested_quantity: number | null;
  urgency: string;
  confidence: string;
}

interface ItemInsights {
  item_name: string;
  category: string;
  current_stock: number;
  unit: string;
  pattern: PatternData;
  prediction: PredictionData;
  last_analyzed: string;
}

const PatternInsights = () => {
  const [searchItem, setSearchItem] = useState('');
  const [selectedItem, setSelectedItem] = useState('');

  // Fetch item insights
  const { data: insights, isLoading, error } = useQuery<ItemInsights>({
    queryKey: ['item-insights', selectedItem],
    queryFn: async () => {
      const response = await api.get(`/api/shopping/insights/${selectedItem}`);
      return response.data;
    },
    enabled: !!selectedItem,
  });

  // Fetch all predictions for search suggestions
  const { data: predictions } = useQuery({
    queryKey: ['all-predictions'],
    queryFn: async () => {
      const response = await api.get('/api/shopping/predictions', {
        params: { limit: 100 }
      });
      return response.data;
    },
  });

  const handleSearch = () => {
    if (searchItem.trim()) {
      setSelectedItem(searchItem.trim().toLowerCase());
    }
  };

  const getConfidenceColor = (confidence: string) => {
    switch (confidence) {
      case 'high': return 'bg-green-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-gray-500';
      default: return 'bg-gray-300';
    }
  };

  const getUrgencyBadge = (urgency: string) => {
    switch (urgency) {
      case 'urgent': return <Badge variant="destructive">Urgent</Badge>;
      case 'this_week': return <Badge variant="default">This Week</Badge>;
      case 'later': return <Badge variant="secondary">Later</Badge>;
      default: return <Badge variant="outline">{urgency}</Badge>;
    }
  };

  const getConfidencePercentage = (confidence: string) => {
    switch (confidence) {
      case 'high': return 90;
      case 'medium': return 60;
      case 'low': return 30;
      default: return 0;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold flex items-center gap-2">
          <BarChart3 className="w-8 h-8" />
          Pattern Insights
        </h2>
        <p className="text-muted-foreground mt-1">
          View detailed usage patterns and predictions for your items
        </p>
      </div>

      {/* Search */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Search Item</CardTitle>
          <CardDescription>
            Enter an item name to view its usage pattern and predictions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input
                placeholder="e.g., milk, rice, tomatoes..."
                value={searchItem}
                onChange={(e) => setSearchItem(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                className="pl-10"
              />
            </div>
            <button
              onClick={handleSearch}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
            >
              View Insights
            </button>
          </div>

          {/* Suggestions */}
          {predictions && predictions.length > 0 && !selectedItem && (
            <div className="mt-4">
              <p className="text-sm text-muted-foreground mb-2">Available items:</p>
              <div className="flex flex-wrap gap-2">
                {predictions.slice(0, 10).map((pred: any) => (
                  <Badge
                    key={pred.id}
                    variant="outline"
                    className="cursor-pointer hover:bg-accent"
                    onClick={() => {
                      setSearchItem(pred.item_name);
                      setSelectedItem(pred.item_name);
                    }}
                  >
                    {pred.item_name}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Loading State */}
      {isLoading && (
        <div className="space-y-4">
          <Skeleton className="h-48 w-full" />
          <Skeleton className="h-48 w-full" />
        </div>
      )}

      {/* Error State */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            No pattern data found for "{selectedItem}". Make sure you've tracked this item's usage for at least 2-3 cycles.
          </AlertDescription>
        </Alert>
      )}

      {/* Insights Display */}
      {insights && !isLoading && (
        <div className="space-y-4">
          {/* Overview Card */}
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-2xl capitalize flex items-center gap-2">
                    {insights.item_name}
                    <Badge variant="outline">{insights.category}</Badge>
                  </CardTitle>
                  <CardDescription className="mt-2">
                    Pattern analysis based on {insights.pattern.data_points} data points
                  </CardDescription>
                </div>
                {getUrgencyBadge(insights.prediction.urgency)}
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Current Stock */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Package className="w-4 h-4" />
                    Current Stock
                  </div>
                  <div className="text-3xl font-bold">
                    {insights.current_stock} {insights.unit}
                  </div>
                </div>

                {/* Predicted Depletion */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Calendar className="w-4 h-4" />
                    Predicted Depletion
                  </div>
                  <div className="text-xl font-semibold">
                    {insights.prediction.depletion_date
                      ? new Date(insights.prediction.depletion_date).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric'
                        })
                      : 'N/A'}
                  </div>
                </div>
              </div>

              {/* Confidence Indicator */}
              <div className="mt-6 space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Prediction Confidence</span>
                  <span className="font-medium capitalize">{insights.prediction.confidence}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Progress 
                    value={getConfidencePercentage(insights.prediction.confidence)} 
                    className="flex-1"
                  />
                  <div className={`w-3 h-3 rounded-full ${getConfidenceColor(insights.prediction.confidence)}`} />
                </div>
                <p className="text-xs text-muted-foreground">
                  {insights.pattern.data_points < 3 && 'Need more data for accurate predictions'}
                  {insights.pattern.data_points >= 3 && insights.pattern.data_points < 5 && 'Building pattern confidence'}
                  {insights.pattern.data_points >= 5 && 'Strong pattern detected'}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Usage Patterns */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Usage Patterns
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Purchase Frequency */}
              <div className="flex items-start justify-between p-4 border rounded-lg">
                <div className="space-y-1">
                  <p className="text-sm font-medium">Purchase Frequency</p>
                  <p className="text-xs text-muted-foreground">
                    How often you typically buy this item
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold">
                    {insights.pattern.purchase_frequency_days 
                      ? Math.round(insights.pattern.purchase_frequency_days)
                      : 'N/A'}
                  </div>
                  <p className="text-xs text-muted-foreground">days</p>
                </div>
              </div>

              {/* Average Purchase Quantity */}
              <div className="flex items-start justify-between p-4 border rounded-lg">
                <div className="space-y-1">
                  <p className="text-sm font-medium">Average Purchase Quantity</p>
                  <p className="text-xs text-muted-foreground">
                    Typical amount you buy
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold">
                    {insights.pattern.avg_quantity_purchased?.toFixed(1) || 'N/A'}
                  </div>
                  <p className="text-xs text-muted-foreground">{insights.unit}</p>
                </div>
              </div>

              {/* Consumption Rate */}
              <div className="flex items-start justify-between p-4 border rounded-lg">
                <div className="space-y-1">
                  <p className="text-sm font-medium">Daily Consumption Rate</p>
                  <p className="text-xs text-muted-foreground">
                    How much you use per day
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold">
                    {insights.pattern.consumption_rate_per_day?.toFixed(2) || 'N/A'}
                  </div>
                  <p className="text-xs text-muted-foreground">{insights.unit}/day</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Prediction Details */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Smart Prediction
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 border rounded-lg">
                  <p className="text-sm text-muted-foreground mb-1">Suggested Purchase</p>
                  <p className="text-2xl font-bold">
                    {insights.prediction.suggested_quantity?.toFixed(1) || 'N/A'} {insights.unit}
                  </p>
                  <p className="text-xs text-muted-foreground mt-2">
                    Based on your typical purchase amount
                  </p>
                </div>

                <div className="p-4 border rounded-lg">
                  <p className="text-sm text-muted-foreground mb-1">Urgency Level</p>
                  <div className="mt-2">
                    {getUrgencyBadge(insights.prediction.urgency)}
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    {insights.prediction.urgency === 'urgent' && 'Buy today or tomorrow'}
                    {insights.prediction.urgency === 'this_week' && 'Buy within 7 days'}
                    {insights.prediction.urgency === 'later' && 'Stock is sufficient'}
                  </p>
                </div>
              </div>

              <div className="text-xs text-muted-foreground text-center pt-4 border-t">
                Last analyzed: {new Date(insights.last_analyzed).toLocaleString()}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default PatternInsights;
