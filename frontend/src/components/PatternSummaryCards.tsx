/**
 * Pattern Summary Cards
 * Displays AI pattern intelligence summary on dashboard
 */

import { useQuery } from '@tanstack/react-query';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { AlertTriangle, Calendar, CheckCircle, TrendingUp } from 'lucide-react';
import api from '@/lib/api';

interface ShoppingPrediction {
  item_name: string;
  category: string;
  urgency: string;
  confidence_level: string;
  data_points_count: number;
}

const PatternSummaryCards = () => {
  // Fetch all predictions
  const { data: predictions, isLoading } = useQuery<ShoppingPrediction[]>({
    queryKey: ['all-predictions'],
    queryFn: async () => {
      const response = await api.get('/api/shopping/predictions');
      return response.data;
    },
  });

  // Calculate counts
  const urgentCount = predictions?.filter(p => p.urgency === 'urgent').length || 0;
  const thisWeekCount = predictions?.filter(p => p.urgency === 'this_week').length || 0;
  const goodCount = predictions?.filter(p => p.urgency === 'later').length || 0;
  const totalTracked = predictions?.length || 0;
  
  // Calculate pattern health (percentage of items with high confidence)
  const highConfidenceCount = predictions?.filter(p => p.confidence_level === 'high').length || 0;
  const patternHealth = totalTracked > 0 ? Math.round((highConfidenceCount / totalTracked) * 100) : 0;

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {[1, 2, 3, 4].map((i) => (
          <Skeleton key={i} className="h-32" />
        ))}
      </div>
    );
  }

  // Don't show if no pattern data yet
  if (totalTracked === 0) {
    return null;
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <TrendingUp className="w-5 h-5 text-primary" />
        <h3 className="text-lg font-semibold">Pattern Intelligence Summary</h3>
      </div>
      
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {/* Urgent */}
        <Card className="hover:shadow-md transition-shadow border-l-4 border-l-red-500">
          <CardContent className="p-4">
            <div className="flex items-start justify-between mb-2">
              <div className="w-8 h-8 rounded-full bg-red-50 flex items-center justify-center">
                <AlertTriangle className="w-4 h-4 text-red-600" />
              </div>
              <span className="text-xs text-muted-foreground">URGENT</span>
            </div>
            <div className="text-3xl font-bold text-red-600">{urgentCount}</div>
            <p className="text-xs text-muted-foreground mt-1">Buy Today</p>
          </CardContent>
        </Card>

        {/* This Week */}
        <Card className="hover:shadow-md transition-shadow border-l-4 border-l-orange-500">
          <CardContent className="p-4">
            <div className="flex items-start justify-between mb-2">
              <div className="w-8 h-8 rounded-full bg-orange-50 flex items-center justify-center">
                <Calendar className="w-4 h-4 text-orange-600" />
              </div>
              <span className="text-xs text-muted-foreground">THIS WEEK</span>
            </div>
            <div className="text-3xl font-bold text-orange-600">{thisWeekCount}</div>
            <p className="text-xs text-muted-foreground mt-1">Buy Soon</p>
          </CardContent>
        </Card>

        {/* Good Stock */}
        <Card className="hover:shadow-md transition-shadow border-l-4 border-l-green-500">
          <CardContent className="p-4">
            <div className="flex items-start justify-between mb-2">
              <div className="w-8 h-8 rounded-full bg-green-50 flex items-center justify-center">
                <CheckCircle className="w-4 h-4 text-green-600" />
              </div>
              <span className="text-xs text-muted-foreground">GOOD</span>
            </div>
            <div className="text-3xl font-bold text-green-600">{goodCount}</div>
            <p className="text-xs text-muted-foreground mt-1">Stock OK</p>
          </CardContent>
        </Card>

        {/* Pattern Health */}
        <Card className="hover:shadow-md transition-shadow border-l-4 border-l-blue-500">
          <CardContent className="p-4">
            <div className="flex items-start justify-between mb-2">
              <div className="w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center">
                <TrendingUp className="w-4 h-4 text-blue-600" />
              </div>
              <span className="text-xs text-muted-foreground">TRACKED</span>
            </div>
            <div className="text-3xl font-bold text-blue-600">{totalTracked}</div>
            <p className="text-xs text-muted-foreground mt-1">{patternHealth}% Health</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PatternSummaryCards;

