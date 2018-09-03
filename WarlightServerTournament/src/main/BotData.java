package main;

public class BotData implements Comparable<BotData>
{
	
	public String botId;
	public String botDir;
	public String botPlayer;
	public double rating;
	
	public BotData(String botId, String botDir, String botPlayerName, double rating)
	{
		
		this.botId = botId;
		
		this.botDir = botDir;;
		
		this.botPlayer = botPlayerName;
		
		this.rating = rating;
	}
	
	

	@Override
	public int compareTo(BotData other) {
		
		
		
		return Double.compare(this.rating, other.rating);
	}
	
	
	

}
