import React, { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { format } from 'date-fns'
import apiService from '../services/api'
import { toast } from 'sonner'
import useLoadingStore from '../store/useLoadingStore'

const HistoricalAnalysis = () => {
  const [analyses, setAnalyses] = useState([])
  const [selectedAnalyses, setSelectedAnalyses] = useState([])
  const { setLoading } = useLoadingStore()

  useEffect(() => {
    const fetchAnalyses = async () => {
      setLoading(true)
      try {
        const response = await apiService.getUserAnalyses()
        if (response.success) {
          setAnalyses(response.data.analyses)
        } else {
          toast.error('Failed to fetch historical analyses.')
        }
      } catch (error) {
        console.error('Error fetching historical analyses:', error)
        toast.error('Error fetching historical analyses.')
      } finally {
        setLoading(false)
      }
    }
    fetchAnalyses()
  }, [setLoading])

  const handleSelectAnalysis = (analysisId) => {
    setSelectedAnalyses(prev => 
      prev.includes(analysisId)
        ? prev.filter(id => id !== analysisId)
        : [...prev, analysisId]
    )
  }

  const renderComparison = () => {
    if (selectedAnalyses.length < 2) {
      return <p className="text-center text-muted-foreground">Select at least two analyses to compare.</p>
    }

    const analysesToCompare = analyses.filter(a => selectedAnalyses.includes(a.id))

    return (
      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Analysis Comparison</CardTitle>
          <CardDescription>Side-by-side comparison of selected brand audits.</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Metric</TableHead>
                {analysesToCompare.map(a => (
                  <TableHead key={a.id}>{a.company_name} ({format(new Date(a.created_at), 'MMM dd, yyyy')})</TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">Brand Health Score</TableCell>
                {analysesToCompare.map(a => (
                  <TableCell key={a.id}>{a.results?.brand_health_score || 'N/A'}</TableCell>
                ))}
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Visual Consistency</TableCell>
                {analysesToCompare.map(a => (
                  <TableCell key={a.id}>{a.results?.visual_analysis?.consistency_score || 'N/A'}%</TableCell>
                ))}
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Overall Sentiment</TableCell>
                {analysesToCompare.map(a => (
                  <TableCell key={a.id}>{a.results?.overall_sentiment || 'N/A'}</TableCell>
                ))}
              </TableRow>
              {/* Add more metrics as needed */}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Historical Analyses</CardTitle>
          <CardDescription>View and compare your past brand audit reports.</CardDescription>
        </CardHeader>
        <CardContent>
          {analyses.length === 0 ? (
            <p className="text-center text-muted-foreground">No historical analyses found.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Select</TableHead>
                  <TableHead>Company Name</TableHead>
                  <TableHead>Website</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Date</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {analyses.map(analysis => (
                  <TableRow key={analysis.id}>
                    <TableCell>
                      <input
                        type="checkbox"
                        checked={selectedAnalyses.includes(analysis.id)}
                        onChange={() => handleSelectAnalysis(analysis.id)}
                        className="form-checkbox h-4 w-4 text-primary rounded"
                      />
                    </TableCell>
                    <TableCell className="font-medium">{analysis.company_name}</TableCell>
                    <TableCell>{analysis.website}</TableCell>
                    <TableCell>
                      <Badge variant={analysis.status === 'completed' ? 'default' : 'secondary'}>
                        {analysis.status}
                      </Badge>
                    </TableCell>
                    <TableCell>{format(new Date(analysis.created_at), 'MMM dd, yyyy HH:mm')}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
      {renderComparison()}
    </div>
  )
}

export default HistoricalAnalysis
